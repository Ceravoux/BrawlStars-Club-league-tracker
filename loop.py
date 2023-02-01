import asyncio
from datetime import datetime, timezone, timedelta
from time import gmtime
import sys, traceback


def to_datetime_from_seconds(s: int):
    """returns a datetime from seconds from epoch"""
    return datetime(*gmtime(s)[:6])


def to_seconds_from_now(dt: datetime):
    now = datetime.now(timezone.utc)
    dt = dt.astimezone(timezone.utc)
    # assert dt >= now, f"{dt} is < {now}"
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
        timezone: timezone = timezone.utc,
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
            timezone for deciding the time of day
            e.g. UTC+8 if you want to start it at 4am UTC-4
        weekday: `tuple[int]`
            0 = Monday, ..., 6 = Sunday
            resumes loop every given weekday at 00:00
        pause: `datetime.timedelta`
            pauses loop for given time after the last loop of the week
            default timedelta(0)
        interval: `int`
            the interval between each call in seconds. (0 ~ 86400)

        """
        self.loop = loop
        self.coro = coro
        self.timezone = timezone
        self.weekday = tuple(sorted(weekday))
        self.to_closest_weekday()

        self.pause = pause
        self.interval = interval

        self._last_index: int = None
        self._task: asyncio.Task = None
        self._sleeping: asyncio.Future = None

    def to_closest_weekday(self):
        self._weekday_index = min(
            range(len(self.weekday)),
            key=lambda x: from_weekday(self.weekday[x], tzinfo=self.timezone),
        )

    def _prepare_time(self): # HACK: do this better
        now = datetime.now(tz=self.timezone)
        print(f"{self.coro.__name__} current weekday: {now.weekday()}; index weekday: {self.weekday[self._weekday_index]}")
        t = 0

        # we initialise a flag so no need to do 
        # now.weekday() == self.weekday[self._weekday_index] twice
        flag = False
        if now.weekday() == self.weekday[self._weekday_index]:
            flag = True
            if self.interval and self._last_index is not None:
                # assume weekday (1 3 5) and 20h interval
                # 2nd loop will happen on day 2 which is not part of sched
                # so we should not return interval for that
                if (now + timedelta(seconds=self.interval)).weekday() in self.weekday:
                    return self.interval

            if self.interval and self._last_index is None:
                self._last_index = self._weekday_index
                return t

        next_day = from_weekday(self.weekday[self._weekday_index], tzinfo=self.timezone)

        if not (flag and self._last_index is None):
            t += to_seconds_from_now(next_day) 

        if self._weekday_index == 0 and self._last_index is not None:
            #XXX
            # if (now + timedelta(seconds=self.pause.total_seconds())) > next_day:
            t += int(self.pause.total_seconds()) 

        self._last_index = self._weekday_index

        if self._last_index == len(self.weekday) - 1:
            self._weekday_index = 0
        else:
            self._weekday_index += 1

        print(f"{self.coro.__name__} next idx", self._weekday_index, "current", self._last_index)         

        return t

    async def _sleep(self):
        self._sleeping = self.loop.create_future()
        t = self._prepare_time()
        print(t, self.coro.__name__)
        self.loop.call_later(t, self._sleeping.set_result, 1)
        await self._sleeping

    async def _loop(self, *args, **kwargs):

        while True:
            await self._sleep()
            try:
                await self.coro(*args, **kwargs)
            except asyncio.CancelledError:
                print("cancelled")
                return

            except Exception as e:
                await self.error(e)

    async def error(self, exception) -> None:
        """Error handler, can be overridden by subclassing."""
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
        print("start", self.coro.__name__)
        self._task = self.loop.create_task(
            self._loop(*args, **kwargs), name=repr(self.coro.__name__)
        )
        return self._task
