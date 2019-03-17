from selenium.webdriver import PhantomJS
from threading import Thread
from queue import Queue
from jinja2 import Template
from os import getcwd
import typing
import asyncio


class Renderer(Thread):
    def __init__(self, template, loop=asyncio.get_event_loop(), width=480, height=480, **kwargs):
        super(Renderer, self).__init__()
        self.template: Template = Template(template)
        self.queue: Queue = Queue()
        self._loop: asyncio.AbstractEventLoop = loop
        self._finished: asyncio.Future = self._loop.create_future()
        self.driver: PhantomJS = PhantomJS(**kwargs)
        self.driver.set_window_size(width=width, height=height)
        self.start()

    def run(self) -> typing.NoReturn:
        while True:
            item: typing.Optional[typing.Tuple] = self.queue.get()
            if item is None:
                break
            future: asyncio.Future = item[0]
            params: typing.Dict = item[1]
            with open("__aiophantom__.html", "w") as r:
                r.write(self.template.render(**params))
            self.driver.get("file://" + getcwd() + "/__aiophantom__.html")
            self._loop.call_soon_threadsafe(future.set_result, self.driver.get_screenshot_as_png())
            self.queue.task_done()
        self._loop.call_soon_threadsafe(self._finished.set_result, None)

    async def render(self, params: typing.Dict) -> bytes:
        future: asyncio.Future = self._loop.create_future()
        self.queue.put((future, params))
        return await future

    async def __aenter__(self):
        return self

    async def close(self) -> typing.NoReturn:
        self.driver.quit()
        self.queue.put(None)
        return await self._finished

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> typing.NoReturn:
        return await self.close()
