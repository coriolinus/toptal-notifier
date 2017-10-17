"get a list of toptal jobs"
import pendulum
import re
from selenium.common.exceptions import NoSuchElementException

from pprint import pformat
from urllib.parse import urljoin

from . import relativetime
from .config import config
from .debug import debug
from .persist import persisted
from .timezone import overlap_between

JOBS = 'https://www.toptal.com/platform/talent/jobs'
TZ_RE = re.compile(
    r"""
    ^\s*                      # leading whitespace
    \(UTC                     # literal
    (?P<sign>[+-])            # sign
    (?P<hours>\d{1,2})        # one or two hours digits
    :                         # literal
    (?P<minutes>\d{2})\)      # two minutes digits
    .*?                       # tz name (but we don't care)
    (?:                       # capture group for overlap clause
        ,\ min\               # literal
        (?P<overlap>\d+)      # some digits of hours of overlap
        \ hours\ overlap      # literal
    )?                        # overlap clause may not exist
    \s*$                      # trailing whitespace
    """,
    re.IGNORECASE | re.VERBOSE
)


def parse_tz_requirement(input):
    """
    Parse a tz requirement.

    TZ requirements are given as base TZ and sometimes a minimum overlap
    in hours. This function parses the requirement string and returns a 2-tuple:
    `(tz_offset: float, overlap: Optional[int])`. `tz_offset` is the time zone offset
    from utc. `overlap` is an integer of required hours of overlap, or `None`.

    Returns `None` if the input could not be parsed as a requirements string.
    """
    match = TZ_RE.match(input)
    if match:
        sign = match.group('sign')
        offset = float(match.group('hours'))
        offset_minutes = float(match.group('minutes'))
        offset += offset_minutes / 60.0
        if sign == '-':
            offset = -offset

        overlap = match.group('overlap')
        if overlap is not None:
            overlap = int(overlap)

        return (offset, overlap)


class Job:
    """
    Class representing a Toptal job
    """

    def __init__(self, element):
        """
        Construct a job from the Selenium `element` representing it.

        `element` must be a Selenium element representing the `div.panel-item`
        at which the job was listed
        """
        title_link = element.find_element_by_css_selector("div.panel-header_title > a")
        self.url = urljoin(JOBS, title_link.get_attribute('href'))
        self.title = title_link.text.strip()

        # extract the details in bulk
        self.details = {}
        for item in element.find_elements_by_css_selector("div.panel_list-item > div.details > div.details-sub_item"):
            k = item.find_element_by_class_name("details-label").text.strip().lower()
            v = item.find_element_by_class_name("details-value").text.strip().lower()
            self.details[k] = v

        for item in element.find_elements_by_css_selector("div.panel_list-item > div.is-full"):
            k = item.find_element_by_class_name("details-label").text.strip().lower()
            if k == 'time zone':
                v = item.find_element_by_class_name("details-value").text.strip().lower()
                self.details[k] = v
            elif k == 'required skills':
                self.skills = {
                    sk.text.strip().lower() for sk
                    in item.find_element_by_class_name("details-value").find_elements_by_tag_name('a')
                }

        # set the job post's estimated timestamp
        self.timestamp_estimate = relativetime.parse(self.details['job posted'], True)

        # set the job's tz and overlap requirements if set
        tz_req = parse_tz_requirement(self.details['time zone'])
        if tz_req is not None:
            self.utc_offset = tz_req[0]
            self.overlap_hours = tz_req[1]
        else:
            self.utc_offset = self.overlap_hours = None

        try:
            self.description = element.find_element_by_class_name(
                "js-full_text"
            ).get_attribute('innerHTML').strip()
        except NoSuchElementException:
            try:
                self.description = element.find_element_by_css_selector(
                    "div.panel_list-item > div.panel_list-text"
                ).get_attribute('innerHTML').strip()
            except NoSuchElementException:
                self.description = "Could not isolate job description; try clicking the URL to investigate"

    def filter(self):
        "True if this job passes all enabled filters"
        if self.overlap_hours and config['tz']['filter']:
            if overlap_between(config['tz']['home'], self.utc_offset) < self.overlap_hours:
                return False
        if config['tags']['filter']:
            if ((len(config['tags']['include']) > 0 and not
                 any(t in self.skills for t in config['tags']['include'])) or
                    any(t in self.skills for t in config['tags']['exclude'])):
                return False

        return True

    def __repr__(self):
        return "<Job at {}>".format(self.url)

    def __str__(self):
        return self.to_string(truncate_desc=True)

    def to_string(self, truncate_desc=False):
        desc = (
            self.description[:75] + '...'
            if truncate_desc and len(self.description) >= 78
            else self.description
        )
        return "{title}\n<{url}>\n\nPosted at: {ts} (est)\nUTC offset: {tz}\nReq. Overlap: {overlap}\n\nSkills: {skills}\n\n{desc}".format(
            title=self.title,
            url=self.url,
            ts=self.timestamp_estimate,
            tz=self.utc_offset,
            overlap=self.overlap_hours,
            skills=pformat(self.skills),
            desc=desc,
        )


def get_jobs(driver):
    """
    Get a list of jobs currently available on Toptal

    driver: a selenium driver instance. It must be currently logged into Toptal.
    """
    with persisted() as pdata:
        try:
            last_scrape = pdata['last_scrape']
        except KeyError:
            last_scrape = None

        scrape_time = pendulum.now()
        driver.get(JOBS)
        debug(driver, 'list of jobs')

        jobs = get_jobs_on_page(driver, [], last_scrape)
        # now update last_scrape
        pdata['last_scrape'] = scrape_time
        return jobs


def get_jobs_on_page(driver, jobs, last_scrape):
    "'Private' method to get a single page's list of jobs"
    for job_element in driver.find_elements_by_css_selector("div.panel > div.panel-item"):
        job = Job(job_element)
        if last_scrape is not None and job.timestamp_estimate < last_scrape:
            return jobs
        else:
            jobs.append(job)

    # the first time we encounter a job whose estimated timestamp is older than
    # our last scrape, we break out. Therefore, if we're here, we need to go to the
    # next page if possible and extend the jobs list
    next_href = None
    for element in driver.find_elements_by_css_selector("div.pagination-switcher a"):
        if element.get_attribute('rel').strip().lower() == 'next':
            next_href = element.get_attribute('href')
            break
    if next_href is not None:
        # recursively add the next page's items
        driver.get(next_href)
        debug(driver, 'next jobs page')
        get_jobs_on_page(driver, jobs, last_scrape)
    # whether or not we went to the next page, return the list of jobs
    return jobs
