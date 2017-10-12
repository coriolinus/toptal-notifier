from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .config import config

SESSION = requests.Session()


def request(method, *args, **kwargs):
    """
    Delegate a request via the requests library with the specified `args` and `kwargs`.

    Saves raw returned data to the `scrapes` folder if `config['save_scrapes']==True`.
    Returns a BeautifulSoup object wtih the returned page.
    """
    response = getattr(SESSION, method)(*args, **kwargs)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html5lib')
    if config['save_scrapes']:
        parsed_url = urlparse(response.url)
        filename = Path("scrapes") / "{scheme}.{netloc}.{dotpath}.html".format(
            scheme=parsed_url.scheme,
            netloc=parsed_url.netloc,
            dotpath=parsed_url.path.replace('/', '.'),
        ).replace('..', '.')
        with open(str(filename), 'w') as output_file:
            output_file.write(soup.prettify())
    return soup


def get(*args, **kwargs):
    return request('get', *args, **kwargs)


def post(*args, **kwargs):
    return request('post', *args, **kwargs)
