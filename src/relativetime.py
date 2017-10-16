import pendulum
import re

PARSER = re.compile(
    r"""
    ^\s*              # start of line whitespace
    (?:About\ )?      # maybe "About"
    (?P<qty>\d+)\     # how many
    (?P<unit>         # what unit of time
        (?:minute)|   # (match literal strings)
        (?:hour)|
        (?:day)
    )s?               # unit of time may be plural
    (?:\ ago)         # "ago"
    \s*$              # end of line whitespace
    """,
    re.IGNORECASE | re.VERBOSE
)


def parse(human_time, round_latest=False):
    """
    Parse a 'humanized' time string.

    Examples of parseable strings:
    - "15 minutes ago"
    - "About 2 hours ago"
    - "1 day ago"

    Returns a pendulum object representing the best guess of the timestamp
    referred to by the string. Note that the error between the actual timestamp
    and the one parsed by this function can be as large 2x the unit of time
    referred to. Therefore, to avoid the erroneous appearance of precision,
    this function zeroes out the units of the timestamp smaller than the
    precision of the input. I.e. `parse_rt("1 day ago")` → a timestamp representing
    midnight yesterday.

    Returns `None` if the input cannot be parsed.

    Sometimes it's more useful to round to the ceiling of the precision instead
    of the floor. To do so, set `round_latest=True`.
    `parse("1 day ago", round_latest=True)` → a timestamp representing
    `23:59:59` yesterday.
    """
    match = PARSER.fullmatch(human_time)
    if match:
        qty = int(match.group('qty'))
        unit = match.group('unit').lower()

        ts = pendulum.now() - pendulum.Interval(**{unit + 's': qty})
        if round_latest:
            return ts.end_of(unit)
        return ts.start_of(unit)
    else:
        return None
