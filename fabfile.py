#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import os
import sys
sys.path.insert(0, os.getcwd())

from fabric.api import *  # noqa


CMD_PYLINT = 'pylint'


@task
def clean():
    """Remove temporary files."""
    for root, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith('.pyc') or name.endswith('~'):
                os.remove(os.path.join(root, name))


@task
def devserver(port=8888, logging='error'):
    """Start the server in development mode."""
    run('python run.py --port=%s --logging=%s' % (port, logging))
