import pendulum
from .config import config


def tz_diff(home, away, on=None):
    """
    Return the difference in hours between the away time zone and home.

    `home` and `away` may be any values which pendulum parses as timezones.
    However, recommended use is to specify the full formal name.
    See https://gist.github.com/pamelafox/986163

    As not all time zones are separated by an integer number of hours, this
    function returns a float.

    As time zones are political entities, their definitions can change over time.
    This is complicated by the fact that daylight savings time does not start
    and end on the same days uniformly across the globe. This means that there are
    certain days of the year when the returned value between `Europe/Berlin` and
    `America/New_York` is _not_ `6.0`.

    By default, this function always assumes that you want the current
    definition. If you prefer to specify, set `on` to the date of your choice.
    It should be a `Pendulum` object.

    This function returns the number of hours which must be added to the home time
    in order to get the away time. For example,
    ```python
    >>> tz_diff('Europe/Berlin', 'America/New_York')
    -6.0
    >>> tz_diff('Europe/Berlin', 'Asia/Kabul')
    2.5
    ```
    """
    if on is None:
        on = pendulum.today()
    diff = (on.timezone_(home) - on.timezone_(away)).total_hours()

    # what about the diff from Tokyo to Honolulu? Right now the result is -19.0
    # it should be 5.0; Honolulu is naturally east of Tokyo, just not so around
    # the date line
    if abs(diff) > 12.0:
        if diff < 0.0:
            diff += 24.0
        else:
            diff -= 24.0

    return diff


def overlap_between(home, away, on=None):
    """
    Return the overlap in work hours between the away time zone and the home time zone.

    The basic computation is simple: assuming a 9 hour work day, and no shifts, the
    overlap is `9.0-abs(tz_diff(home, away))`.

    Some workers are willing to shift their schedule to better accommodate remote clients.
    They can configure this in `config.toml`, in the `[notify.tz]` table, by setting the
    following values:

    - `shift_early: int` the number of hours you're willing to shift your schedule earlier
        to increase overlap with the client. This is most useful for accepting clients east
        of your location. Default: `0`
    - `shift_late: int` the number of hours you're willing to shift your schedule later to
        increase overlap with the client. This is most useful for accepting clients west of
        your location. Default: `0`
    """
    diff = tz_diff(home, away, on)
    if diff < 0:
        # the away location is west of the home location, therefore later
        return 9.0 + diff + config['tz']['shift_late']
    else:
        # the away location is east of the home location, therefore earlier
        return 9.0 - diff + config['tz']['shift_early']
