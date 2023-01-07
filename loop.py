import asyncio
from datetime import datetime, timezone, timedelta
from time import gmtime
import sys, traceback


def to_datetime_from_seconds(s: int):
    """returns a datetime from seconds from epoch"""
    return datetime(*gmtime(s)[:6])


def to_seconds_from_epoch(dt: datetime):
    dt = dt.astimezone(timezone.utc)
    return round((dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())


def to_seconds_from_now(dt: datetime):
    now = datetime.now(timezone.utc)
    dt = dt.astimezone(timezone.utc)
    assert dt >= now, "dt is < now"
    return round((dt - now).total_seconds())


def from_weekday(
    weekday: int, hour: int = 0, minute: int = 0, second: int = 0, *, tzinfo: timezone
):
    now = datetime.now(tzinfo)
    today = now.weekday()
    return now + timedelta(
        days=(weekday - today + (7 if weekday < today else 0)),
        hours=(hour - now.hour),
        minutes=(minute - now.minute),
        seconds=second - now.second,
        microseconds=-now.microsecond,
    )


class Loop:

    __slots__ = (
        "timezone",
        "loop",
        "coro",
        "_weekday_index",
        "_last_index",
        "_task",
        "interval",
        "pause",
        "_sleeping",
        "weekday",
    )

    def __init__(
        self,
        *,
        loop: asyncio.AbstractEventLoop,
        coro,
        timezone: timezone,
        weekday: tuple[int],
        pause: timedelta = timedelta(0),
        interval: int = None,
    ) -> None:
        """
        A loop with custom delays and pauses.

        Parameters
        ----------
        loop: `asyncio.AbstractEventLoop`
            event loop
        coro: `Coroutine`
            the coroutine to be awaited on this loop
        timezone: `datetime.tzinfo`
            timezone for deciding the time
        weekday: `Sequence[int]`
            resumes loop every given weekday at 00:00
        pause: `datetime.timedelta`
            pauses loop for given time after the last loop of the week
            default timedelta(0)
        interval: `int`
            the interval between each call in seconds.

        """
        self.loop = loop
        self.coro = coro
        self.timezone = timezone
        self.weekday = tuple(sorted(weekday))

        self._weekday_index = min(
            range(len(weekday)),
            key=lambda x: from_weekday(self.weekday[x], tzinfo=self.timezone),
        )
        self.pause = pause
        self.interval = interval
        
        self._last_index: int
        self._task: asyncio.Task
        self._sleeping: asyncio.Future

    def _prepare_time(self):
        now = datetime.now(tz=self.timezone)
        if now.weekday() == self.weekday[self._weekday_index]:
            if self.interval:
                return self.interval
            t = 0
        else:
            t = to_seconds_from_now(
                from_weekday(self.weekday[self._weekday_index], tzinfo=self.timezone)
            )
        self._last_index = self._weekday_index

        if self._last_index == len(self.weekday) - 1:
            t += round(self.pause.total_seconds())
            self._weekday_index = 0
        else:
            self._weekday_index += 1

        return t

    async def _sleep(self):
        self._sleeping = self.loop.create_future()
        t = self._prepare_time()
        self.loop.call_later(t, self._sleeping.set_result, 1)
        await self._sleeping

    async def _loop(self, *args, **kwargs):

        while True:
            try:
                await self.coro(*args, **kwargs)
            except asyncio.CancelledError:
                print("cancelled")
                return

            except Exception as e:
                await self.error(e)

            else:
                await self._sleep()

    async def error(self, exception) -> None:
        """Error handler, can be overridden by subclassing."""
        exception = exception[-1]
        print(
            f"Unhandled exception in internal background task {self.coro.__name__!r}.",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(exception),
            exception,
            exception.__traceback__,
            file=sys.stderr,
        )
        return

    def start(self, *args, **kwargs) -> asyncio.Task:
        if self._task is not None and not self._task.done():
            print(f"{self._task} is running!")
            return
        print("start")
        self._task = self.loop.create_task(
            self._loop(*args, **kwargs), name=repr(self.coro.__name__)
        )
        return self._task
