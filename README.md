# Toptal notifier

This notifier is intended to be run periodically via cron or similar. On each run, it performs the following actions:

1. Scrape the toptal.com list of jobs
2. Compare to a database of known jobs
3. Filter according to parameters defined in a config file
4. Send an email for new jobs which meet configured criteria

## Configuration

Configuration is accomplished via the file `config.toml` in the project root. If this file is not present, or any configuration value is missing, the values in `defaults.toml` are used instead.

`[notify]` configures general parameters for the program.

- `email_address: str` your email address. This is where notifications will be sent.
- `debug_output: bool` if `True`, emit debugging screenshots and html. Default: `False`

`[notify.auth]` configures your toptal authentication

- `username: str` your toptal username
- `password: str` your toptal password

`[notify.persist]` configures file persistence.

- `path: str` where to put the persistence file. Default: `"persist.toml"`

`[notify.email]` configures the protocol with which the program sends mail to you. This is assumed to be an SMTP server capable of TLS.

- `host: str` the smtp host used to send mail
- `port: int` the smtp port for your email host
- `from_address: str` the email address from which sent emails will originate

`[notify.tags]` is a sub-table defining which tags you're interested in. Jobs are tagged according to various skills and frameworks.

- `filter: bool` if `True`, filter potential jobs according to their tags. Default: `False`
- `exclude: List[str]` if any item from this list is present in a job's tags, the job will not be forwarded to the user. Default: `[]`
- `include: List[str]` if no items from this list are present in a job's tags, the job will not be forwarded to the user. Special case: if this list is empty, no jobs will be rejected. Default: `[]`

`[notify.tz]` is a sub-table defining your time-zone availability. Many jobs specify a time zone and a certain degree of overlap required. This table's configuration defines how jobs will be filtered according to time zone availability.

The default work period is assumed to be from 8am to 5pm for both the coder and the client. The default workday is assumed to contain 8 hours. This means that a coder and client one timezone apart are assumed to have eight hours of overlap. Hours of overlap are computed by computing the number of hours of difference between the two time zones, and then accounting for the shifts the coder is willing to accommodate.

- `filter: bool` if `True`, jobs will be filtered according to time zone availability. Default: `False`
- `home: str` your home time zone. This must be a value present in `pytz.all_timezones`. Default: `"UTC"`
- `shift_early: int` the number of hours you're willing to shift your schedule earlier to increase overlap with the client. This is most useful for accepting clients east of your location. Default: `0`
- `shift_late: int` the number of hours you're willing to shift your schedule later to increase overlap with the client. This is most useful for accepting clients west of your location. Default: `0`

### Selenium Configuration

This project depends on Selenium and [Chrome](https://www.google.com/chrome/browser/desktop/index.html). In the future things may get more user-friendly, but for now, you need to specify the precise locations of both your chrome executable and the selenium [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). Do so with the following table in `config.toml`:

`[selenium]`

- `chrome: str` absolute path to chrome executable
- `driver: str` absolute path to chromedriver executable
