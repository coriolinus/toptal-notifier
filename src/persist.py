"Handle data persistence for the notifier"

import pendulum
import toml
from contextlib import contextmanager
from datetime import datetime
from .config import config


def get_persisted():
    """
    Get nearly arbitrary data which this program wants to persist.
    """
    try:
        with open(config['persist']['path'], 'r') as persistfile:
            return toml.loads(persistfile.read())
    except FileNotFoundError:
        return None


def persist(data_dict):
    """
    Persist nearly arbitrary data.

    Mainly, this program needs to persist the timestamp at which it
    was last run, to know how far back to look when looking through
    the jobs list. Adding a full database would be overkill.

    The "nearly arbitrary" bit is that the entries in `data_dict`
    must be TOML-serializeable. See <https://github.com/toml-lang/toml>
    for a precise definition of what that means.
    """
    with open(config['persist']['path'], 'w') as persistfile:
        return persistfile.write(toml.dumps(data_dict))


@contextmanager
def persisted():
    """
    Context manager for persistent data.

    Use like:

    ```python
    from .persist import persisted
    with persisted() as pdata:
        last_access = pdata['last_access']
        # do something interesting here
        pdata['last_access'] = datetime.now()
    ```

    - if no persistent data file found, `pdata` will be an empty dictionary
    - all datetimes discovered in the persistent data are converted to `pendulum` objects
    - updated values are written back to the file on exiting the context manager
    """
    pdata = get_persisted()
    if persisted is None:
        pdata = {}
    for name, value in pdata.items():
        if isinstance(value, datetime):
            pdata[name] = pendulum.instance(value)
    try:
        yield pdata
    finally:
        persist(pdata)
