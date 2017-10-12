"log into toptal"

import requests
from bs4 import BeautifulSoup


def login(username, password):
    "Log into Toptal via the users/login endpoint"
    # step 1: request the login page to get the CSRF token
    response = requests.get("https://www.toptal.com/users/login",
                            timeout=5).raise_for_status()
    login_page = BeautifulSoup(response.text, 'html5lib')
