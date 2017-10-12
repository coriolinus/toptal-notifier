"log into toptal"

from . import http


def login(username, password):
    "Log into Toptal via the users/login endpoint"
    # step 1: request the login page to get the CSRF token
    login_page = http.get("https://www.toptal.com/users/login",
                          timeout=5)
