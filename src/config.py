import collections
import toml
# from .errors import BadConfiguration

DEFAULTS_FILENAME = "defaults.toml"
FILENAME = "config.toml"


def update(d, u):
    # turns out that updating nested dicts is more complicated
    # than it might appear at first glance
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


with open(DEFAULTS_FILENAME, 'r') as defaults_file:
    config = toml.loads(defaults_file.read())

with open(FILENAME, 'r') as config_file:
    update(config, toml.loads(config_file.read()))

selenium = config['selenium']
config = config['notify']
