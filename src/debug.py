from datetime import datetime
from pathlib import Path
from .config import config


def debug(driver, text=None):
    if config['debug_output']:
        if text is None:
            filename_base = datetime.now().isoformat().replace(':', '')
        else:
            filename_base = "{dt}_{text}".format(
                dt=datetime.now().isoformat().replace(':', ''),
                text=text.replace(' ', '_').replace(':', ''),
            )
        screenshot_filename = Path('screens') / (filename_base + '.png')
        html_filename = Path('scrapes') / (filename_base + '.html')

        driver.save_screenshot(str(screenshot_filename))
        with open(str(html_filename), 'w') as outf:
            outf.write(driver.page_source)
