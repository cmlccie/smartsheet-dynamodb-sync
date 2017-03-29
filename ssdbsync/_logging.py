#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Docstring."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
import os


# Constants
LOG_LEVEL = os.getenv('LOG_LEVEL', "WARNING")


# Initialize module logging
logger = logging.getLogger(__name__)


# Helper Functions
def is_valid_log_level(log_level_name):
    return log_level_name in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def get_log_level(log_level_name):
    return getattr(logging, log_level_name)


# Core Functionality
def initialize_logging(log_level_name=LOG_LEVEL):
    """Initialize the script logging
    
    Args:
        module_name(basestring): The name of the module for which logging 
            should be initialized.
        log_level_name(basestring): The logging level that should be set.  
            Must be one of the following:
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    
    """
    assert is_valid_log_level(log_level_name)

    root_logger = logging.getLogger()
    root_logger.setLevel(get_log_level(log_level_name))
    root_logger.addHandler(logging.NullHandler())


def enable_console_logging(log_level_name="INFO"):
    """Enable logging to the console, for the named module.
    
    Args:
        log_level_name(basestring): The logging level that should be set.  
            Must be one of the following:
            "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    
    """
    assert is_valid_log_level(log_level_name)

    root_logger = logging.getLogger()

    level = get_log_level(log_level_name)
    root_logger.setLevel(level)

    # Create and add console handler to module logger
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('[%(levelname)-8s] %(name)s:  %(message)s'))
    root_logger.addHandler(console_handler)
