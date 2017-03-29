#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Data model for extracted table data."""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import collections
import logging
from collections import OrderedDict


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


# Initialize module logging
logger = logging.getLogger(__name__)


# Core Functionality
class DataTable(object):
    """Data model for extracted table data."""

    def __init__(self, id):
        logger.info("Initializing DataTable object '{}'".format(id))

        super(DataTable, self).__init__()
        self._id = id if isinstance(id, basestring) else str(id)
        self._columns = OrderedDict()
        self._rows = []

    @property
    def id(self):
        """Table ID."""
        return self._id

    def add_column(self, id, title):
        """Validate and add column id to title mapping."""
        logger.debug("Adding Column: "
                           "{id}, {title}".format(id=id, title=title))

        id = id if isinstance(id, basestring) else str(id)
        assert isinstance(id, basestring)
        assert isinstance(title, basestring)

        if id in self._columns.keys():
            logger.warning("Duplicate Column ID: {}".format(id))
        if title in self._columns.values():
            logger.warning("Duplicate Column Title: {}\n"
                                 "This table will not serialize to JSON well."
                                 "".format(title))
        if title == 'id':
            logger.warning("Column with Title 'id' found.\n"
                                 "This table will not serialize to JSON well.")

        self._columns[id] = title

    @property
    def columns(self):
        """OrderedDict \{'column id': 'column title'\}"""
        return self._columns.copy()

    def add_row(self, row):
        """Validate and add row to DataTable.

        Args:
            row(dict): With 'id' and 'data' keys.
                'id' should map to a string that uniquely identifies the row.
                'data' should map to an dict containing 'column_id' to cell
                value mappings.

        """
        logger.debug("Adding Row: {!r}".format(row))
        assert isinstance(row, dict)
        assert 'id' in row.keys() and isinstance(row['id'], basestring)
        assert 'data' in row.keys() and isinstance(row['data'], dict)
        self._rows.append(row)

    def iterrows(self):
        for row in self._rows:
            yield row
