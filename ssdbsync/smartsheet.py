#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SmartSheet API interactions wrapper."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
from collections import OrderedDict

import smartsheet

from .datatable import DataTable


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


# Helper Functions
def cell_is_not_empty(row, column_id):
    """Check whether the value of a cell in a SmartSheet row is empty."""
    for cell in row.cells:
        if cell.column_id == column_id:
            if cell.value:
                return True
            else:
                return False


# Core Functionality
class SmartSheetInterface(object):
    """Package interface for working with SmartSheet spreadsheets."""

    def __init__(self, access_token):
        """Init a new SmartSheetConnection object."""
        self._logger = logging.getLogger(__name__)
        self._logger.info("Initializing a new SmartSheetConnection object.")
        
        super(SmartSheetInterface, self).__init__()
        self.__access_token = access_token
        self._sdk = smartsheet.Smartsheet(access_token=self.__access_token)

        assert self.connected

    @property
    def connected(self):
        """SmartSheet connection test."""
        self._logger.info("Beginning SmartSheet connection test.")
        try:
            user = self._sdk.Users.get_current_user()
        except smartsheet.exceptions.SmartsheetException as e:
            self._logger.critical("SmartSheet connection test FAILED; "
                                  "exception raised.", exc_info=True)
            return False
        else:
            if isinstance(user, smartsheet.models.Error):
                self._logger.critical("SmartSheet connection test FAILED; "
                                      "returned error:\n"
                                      "{}.".format(user.to_json()))
                return False
            else:
                self._logger.info("Connected to SmartSheet with user account: "
                                  "{firstName} {lastName} "
                                  "<{email}>".format(**user.to_dict()))
                return True

    def get_sheet(self, sheet_id):
        """Retrieve a sheet object.

        Args:
            sheet_id(str): The SmartSheet sheet ID of the sheet to be returned.

        Returns:
            smartsheet.models.Sheet: The SmartSheet sheet object.

        """
        self._logger.info("Getting the SmartSheet object for "
                          "Sheet ID '{}'.".format(sheet_id))
        return self._sdk.Sheets.get_sheet(sheet_id, page=None, page_size=None)

    def extract_data(self, sheet_id):
        """Extract and return the data from the SmartSheet with sheet ID.

        Args:
            sheet_id(str): The SmartSheet sheet ID of the sheet.

        Returns:
            DataTable: The data extracted from the SmartSheet.

        """
        self._logger.info("Extracting data from Sheet ID {}.".format(sheet_id))

        sheet = self.get_sheet(sheet_id)
        data = DataTable(sheet_id)

        # Extract column id to title mappings, and identify the primary column.
        primary_column_id = None
        for column in sheet.columns:
            data.add_column(column.id, column.title)
            if not primary_column_id and column.primary:
                primary_column_id = column.id

        # Extract row data
        for sheet_row in sheet.rows:
            # Only add rows where the primary column is not empty
            if cell_is_not_empty(sheet_row, primary_column_id):
                row = OrderedDict()
                row['id'] = sheet_row.id

                row_data = OrderedDict()
                for cell in sheet_row.cells:
                    row_data[str(cell.column_id)] = cell.value
                row['data'] = row_data

                data.add_row(row)

        return data
