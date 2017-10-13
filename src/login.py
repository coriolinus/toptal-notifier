"log into toptal"
from .config import config
from .debug import debug

LOGIN_BEGIN = 'https://www.toptal.com/users/login'


def login(driver):
    """
    Log into Toptal via the users/login endpoint

    driver: a selenium driver instance
    """
    driver.get(LOGIN_BEGIN)

    debug(driver, 'pre-login')

    email_field = driver.find_element_by_id("user_email")
    pw_field = driver.find_element_by_id("user_password")

    email_field.clear()
    email_field.send_keys(config['auth']['username'])

    pw_field.clear()
    pw_field.send_keys(config['auth']['password'])

    # this is actually the "Login" button
    driver.find_element_by_id("save_new_user").click()

    debug(driver, 'post-login')
