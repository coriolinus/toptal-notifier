import toml
from .errors import BadConfiguration

DEFAULTS_FILENAME = "defaults.toml"
FILENAME = "config.toml"

with open(DEFAULTS_FILENAME, 'r') as defaults_file:
    config = toml.loads(config_file.read())
with open(FILENAME, 'r') as config_file:
    config.update(toml.loads(config_file.read()))

if 'email' not in config['notify'].keys():
    raise BadConfiguration("[notify.email] table not found in config.toml")
