#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Amazon AWS DynamoDB API interactions wrapper."""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
import os

import boto3

from ._datatable import DataTable


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


# Initialize module logging
logger = logging.getLogger(__name__)


# Constants
DEFAULT_READ_CAPACITY_UNITS = int(os.getenv('DEFAULT_READ_CAPACITY_UNITS', 1))
DEFAULT_WRITE_CAPACITY_UNITS = int(os.getenv('DEFAULT_WRITE_CAPACITY_UNITS', 1))


# Core Functionality
class DynamoDBInterface(object):
    """Package interface for working with DynamoDB tables."""

    def __init__(self):
        """Init a new DynamoDBInterface object."""
        logger.info("Initializing a new DynamoDBInterface object.")

        self._dynamodb = boto3.resource('dynamodb')

    def create_table(self, table_name,
                     read_capacity_units=DEFAULT_READ_CAPACITY_UNITS,
                     write_capacity_units=DEFAULT_WRITE_CAPACITY_UNITS):
        """Create a DynamoDB table.
        
        Args:
            table_name(basestring): The name of the table to be created.
            read_capacity_units(int): The AWS read capacity units.
            write_capacity_units(int): The AWS write capacity units.
        
        """
        logger.info("Creating a new DynamoDB table '{}'.".format(table_name))
        assert isinstance(table_name, basestring)
        assert isinstance(read_capacity_units, int) \
               and read_capacity_units >= 1
        assert isinstance(write_capacity_units, int) \
               and write_capacity_units >= 1

        # Create the table
        table = self._dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': read_capacity_units,
                'WriteCapacityUnits': write_capacity_units
            }
        )
        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        return table

    def get_table(self, table_name):
        """Get the DynamoDB table."""
        logger.info("Getting the DynamoDB table '{}'.".format(table_name))
        assert isinstance(table_name, basestring)

        # Retrieve the table, if it exists, otherwise create a new one.
        if table_name in [table.name for table in self._dynamodb.tables.all()]:
            return self._dynamodb.Table(table_name)
        else:
            logger.info("Table '{}' not found.".format(table_name))
            return self.create_table(table_name)

    def update_table(self, table_name, data):
        """Update DynamoDB table with data.

        Args:
            table_name(basestring): The name of the table to be updated.
            data(DataTable): The data for the update.

        """
        logger.info("Beginning table update.")
        assert isinstance(table_name, basestring)
        assert isinstance(data, DataTable)

        table = self.get_table(table_name)

        with table.batch_writer() as batch:
            for row in data.iterrows():
                logger.debug("Adding Item ID: {id}".format(**row))
                batch.put_item(Item=row)
        logger.info("Table update complete.")
