#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""SmartSheet Sync Lambda Function."""


import logging
import os

import boto3
import smartsheet as smartsheet_sdk


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2016 Cisco Systems, Inc."
__license__ = "MIT"


# Setup logging
logger = logging.getLogger()
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logger.setLevel(logging.INFO)
logger.addHandler(NullHandler())


# Constants
SHEET_ID = os.getenv('SHEET_ID')
READ_CAPACITY_UNITS = int(os.getenv('READ_CAPACITY_UNITS'))
WRITE_CAPACITY_UNITS = int(os.getenv('WRITE_CAPACITY_UNITS'))
COLUMN_TITLES_ID = '0'


# Setup SmartSheet connection
smartsheet = smartsheet_sdk.Smartsheet()
primary_column_id = None


# Setup DynamoDB connection
dynamodb = boto3.resource('dynamodb')


# Helper functions
def enable_logging_to_console(log_level=logging.WARNING):
    """Enable console logging."""
    global console_handler
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter('[%(levelname)-8s] %(name)s:  %(message)s'))
    root_logger.addHandler(console_handler)


def test_smartsheet_connection():
    """Test the connection to the SmartSheet API."""
    current_user = smartsheet.Users.get_current_user()
    logger.info("Connected to SmartSheet with User Account: {firstName} "
                "{lastName} <{email}>".format(**current_user.to_dict()))


def get_primary_column_id(sheet):
    global primary_column_id
    for column in sheet.columns:
        if column.primary:
            primary_column_id = column.id


def primary_column_is_not_empty(row):
    for cell in row.cells:
        if cell.column_id == primary_column_id:
            if cell.value:
                return True
            else:
                return False


# Core functions
def get_smartsheet():
    """Retrieve the SmartSheet object."""
    logger.info("Getting the SmartSheet object for "
                "Sheet ID '{}'.".format(SHEET_ID))
    return smartsheet.Sheets.get_sheet(SHEET_ID, page=None, page_size=None)


def extract_data(sheet):
    """Extract the data from the SmartSheet."""
    logger.info("Extracting data.")
    data = []

    # Create column id to title mapping and store as item with COLUMN_TITLES_ID
    column_data = {str(column.id): column.title for column in sheet.columns}
    column_data['id'] = COLUMN_TITLES_ID
    data.append(column_data)

    # Extracted and append data from the SmartSheet Rows
    get_primary_column_id(sheet)
    for row in sheet.rows:
        if primary_column_is_not_empty(row):
            row_data = {str(cell.column_id): cell.value for cell in row.cells}
            row_data['id'] = str(row.id)
            data.append(row_data)

    return data


def create_table():
    """Create the DynamoDB table."""
    logger.info("Creating a new DynamoDB table '{}'.".format(SHEET_ID))
    table = dynamodb.create_table(
        TableName=SHEET_ID,
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
            'ReadCapacityUnits': READ_CAPACITY_UNITS,
            'WriteCapacityUnits': WRITE_CAPACITY_UNITS
        }
    )
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=SHEET_ID)
    return table


def get_table():
    """Get the DynamoDB table."""
    logger.info("Getting the DynamoDB table '{}'.".format(SHEET_ID))
    if SHEET_ID not in [table.name for table in dynamodb.tables.all()]:
        logger.info("Table '{}' not found.".format(SHEET_ID))
        return create_table()
    return dynamodb.Table(SHEET_ID)


def update_table(table, data):
    logger.info("Begin batch table update.")
    with table.batch_writer() as batch:
        for data_row in data:
            logger.debug("Adding Item ID: {id}".format(**data_row))
            batch.put_item(Item=data_row)
    logger.info("Batch table update complete.")


# AWS Lambda Funtion
def lambda_handler(event, context):
    sheet = get_smartsheet()
    table = get_table()
    data = extract_data(sheet)
    update_table(table, data)

    if __name__ == "__main__":
        return (sheet, data, table)
    else:
        return 'SmartSheet Sync to Table {} Successful'.format(SHEET_ID)


# Main
if __name__ == "__main__":
    enable_logging_to_console(logging.INFO)
    test_smartsheet_connection()
    sheet, data, table = lambda_handler({}, {})
