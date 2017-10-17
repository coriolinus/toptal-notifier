#!/usr/bin/env python3
"""
notify.py - get notifications when new toptal jobs show up
"""

from contextlib import closing
from selenium import webdriver
from src import config
from src.email import send_jobs
from src.jobs import get_jobs
from src.login import login
from sys import stdout, stderr


def get_driver_chrome():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    # the following line causes things to fail for reasons which remain mysterious
    # options.binary_location = config.selenium['chrome']
    driver = webdriver.Chrome(executable_path=config.selenium['driver'], chrome_options=options)
    driver.set_window_size(1200, 900)
    return driver


def get_driver_phantomjs():
    driver = webdriver.PhantomJS()
    driver.set_window_size(1200, 900)
    return driver


def notify():
    with closing(get_driver_phantomjs()) as driver:
        login(driver)
        jobs = get_jobs(driver)

    print("Found {} total jobs".format(len(jobs)))
    jobs = [j for j in jobs if j.filter()]
    print("Found {} valid jobs".format(len(jobs)))

    if len(jobs) > 0:
        print("Sending email... ", end='')
        stdout.flush()
        try:
            send_jobs(jobs)
        except Exception as e:
            print('failed!')
            print("{}: {}".format(e.__class__, str(e)), file=stderr)
        else:
            print("done!")


if __name__ == '__main__':
    notify()
