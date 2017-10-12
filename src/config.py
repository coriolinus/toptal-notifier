import toml
# from .errors import BadConfiguration

DEFAULTS_FILENAME = "defaults.toml"
FILENAME = "config.toml"

with open(DEFAULTS_FILENAME, 'r') as defaults_file:
    config = toml.loads(defaults_file.read())
with open(FILENAME, 'r') as config_file:
    config.update(toml.loads(config_file.read()))

config = config['notify']

# if 'email' not in config.keys():
#     raise BadConfiguration("[notify.email] table not found in config.toml")
