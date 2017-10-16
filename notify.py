#!/usr/bin/env python3
"""
notify.py - get notifications when new toptal jobs show up
"""

from contextlib import closing
from selenium import webdriver
from src import config
from src.login import login
from src.jobs import get_jobs


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    # the following line causes things to fail for reasons which remain mysterious
    # options.binary_location = config.selenium['chrome']
    driver = webdriver.Chrome(executable_path=config.selenium['driver'], chrome_options=options)
    driver.set_window_size(1200, 900)
    return driver


def notify():
    with closing(get_driver()) as driver:
        login(driver)
        jobs = get_jobs(driver)
        print("Found {} total jobs".format(len(jobs)))
        if len(jobs) > 0:
            print("First job:")
            print(str(jobs[0]))


if __name__ == '__main__':
    notify()
