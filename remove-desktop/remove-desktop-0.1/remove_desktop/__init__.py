#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:et

"""
remove_desktop

This module sets up the main interface for remove_desktop package.

"""

# This package contains 2 useful modules: remove_desktop and utils;
# we include them in the interface:
from . import remove_desktop
from . import utils

from .remove_desktop import (defaults, Locator, validator, parser,
parser_stage_2, worker)

__state__ = "development"
