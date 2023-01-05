import asyncio
from datetime import datetime, timezone, timedelta
from time import gmtime


def to_datetime_from_seconds(s:int):
    """returns a datetime from seconds from epoch"""
    return datetime(*gmtime(s)[:6])
 
def to_seconds_from_epoch(dt: datetime):
    dt = dt.astimezone(timezone.utc)
    return round((dt - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds())


def to_seconds_from_now(dt: datetime):
    now = datetime.now(timezone.utc)
    dt = dt.astimezone(timezone.utc)
    assert dt > now
    return round((dt - now).total_seconds())


def from_weekday(
    weekday: int, hour: int = 0, minute: int = 0, second: int = 0, *, tzinfo: timezone
):
    now = datetime.now(tzinfo)
    today = now.weekday()
    return now + timedelta(
        days=(
            weekday
            - today
            + (7 if weekday < today else 0)
        ),
        hours=(hour - now.hour),
        minutes=(minute - now.minute),
        seconds=second - now.second,
        microseconds=-now.microsecond,
    )

class Loop:

    # __slots__ = ("times", "loop", "coro", "_weekday_index",
    #              "next_weekday_index", "_stop_next_weekday_index", "_task",
    #              "_sleeping", "_before_loop")
    def __init__(
        self,
        *,
        loop: asyncio.AbstractEventLoop,
        coro,
        timezone: timezone,
        weekday: tuple[int],
        pause: timedelta = timedelta(0),
        interval: int = None
    ) -> None:
        """
        A loop with custom delays and pauses.

        Parameters
        ----------
        weekdays: `Sequence[int]`
            resumes loop every given weekday at 00:00
        timezone: `datetime.tzinfo`
            timezone for deciding the time
        pause: `datetime.timedelta`
            pauses loop for given time after the last loop of the week
            default timedelta(0)
        interval: `int`
            the interval between each call in seconds.

        """
        self.loop = loop
        self.coro = coro
        self._weekday_index = 0
        self.next_weekday_index = 1

        self._task = None

        self._sleeping: asyncio.Future

        self.timezone = timezone
        self.weekday = tuple(sorted(weekday))
        self.pause = pause

        self.interval = interval

    def _prepare_time(self):
        now = datetime.now(tz=self.timezone)
        if now.weekday() == self.weekday[self._weekday_index] and self.interval:
            return self.interval

        t = to_seconds_from_now(
            from_weekday(self.weekday[self._weekday_index], tzinfo=self.timezone)
        )

        self._weekday_index = self.next_weekday_index

        if self.next_weekday_index == 0:
            t += round(self.pause.total_seconds())

        if len(self.weekday) - 1 > self._weekday_index:
            self.next_weekday_index += 1
        else:
            self.next_weekday_index = 0

        return t

    async def _sleep(self):
        self._sleeping = self.loop.create_future()
        t = self._prepare_time()
        print("sleep for:", t)
        self.loop.call_later(t, self._sleeping.set_result, 1)
        await self._sleeping

    async def _loop(self, *args, **kwargs):

        while True:
            print("start sleep")
            # await foo()
            await self._sleep()
            print("after fut")
            try:
                await self.coro(*args, **kwargs)
                # await foo()
            except asyncio.CancelledError:
                print("cancelled")
                return

            except Exception as e:
                # await self.error(err)
                raise e


    async def error(self, *args) -> None:
        return

    def start(self, *args, **kwargs) -> asyncio.Task:
        if self._task is not None and not self._task.done():
            raise RuntimeError("Task is already launched and is not completed.")
        print("start")
        self._task = self.loop.create_task(self._loop(*args, **kwargs), name="loop task")
        return self._task

