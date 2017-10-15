"Handle data persistence for the notifier"

import toml
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
