#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Basic run script"""
from settings import settings

import asyncio

from tornado.platform.asyncio import AsyncIOMainLoop

from get_it_done.utils import run_sync
import chronos
import tornado.autoreload
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.web
from tornado.options import options

from get_it_done.tasks.gmail_gtd import task_gmail_messages_next_cycle, task_chronos_test
from get_it_done.urls import url_patterns


class TornadoApplication(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **settings)


def main():
    app = TornadoApplication()
    app.listen(options.port)

    chronos.setup(tornado.ioloop.IOLoop.current())
    chronos.schedule('test_task', chronos.every(5).seconds, lambda: run_sync(task_chronos_test), start=True)
    chronos.start(False)

    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
