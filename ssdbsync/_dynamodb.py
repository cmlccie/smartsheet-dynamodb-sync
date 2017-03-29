#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Amazon AWS DynamoDB API interactions wrapper."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import boto3


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


# Constants
DEFAULT_READ_CAPACITY_UNITS = int(os.getenv('DEFAULT_READ_CAPACITY_UNITS'))
DEFAULT_WRITE_CAPACITY_UNITS = int(os.getenv('DEFAULT_WRITE_CAPACITY_UNITS'))





class DynamoDBInterface(object):
    """Package interface for working with DynamoDB tables."""

    def __init__(self):
        self._dynamodb = boto3.resource('dynamodb')
