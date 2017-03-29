#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""SmartSheet Sync Lambda Function."""
"""SmartSheet-to-DynamoDB Sync Lambda Function."""


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
import os
import sys
from base64 import b64decode

import boto3

import ssdbsync


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)


# Constants
ENCRYPTED_SMARTSHEET_ACCESS_TOKEN = os.getenv('ENCRYPTED_SMARTSHEET_ACCESS_TOKEN')
SHEET_ID = os.getenv('SHEET_ID')
COLUMN_TITLES_ID = '0'


# Initialize logging
ssdbsync.initialize_logging()
logger = logging.getLogger(__name__)


# Initialize AWS Key Management System (KMS) interface
kms = boto3.client('kms')


# Initialize SmartSheet interface
smartsheet_access_token = kms.decrypt(
    CiphertextBlob=b64decode(ENCRYPTED_SMARTSHEET_ACCESS_TOKEN))['Plaintext']
smartsheet = ssdbsync.SmartSheetInterface(smartsheet_access_token)


# Initialize DynamoDB interface
dynamodb = ssdbsync.DynamoDBInterface()


# Main
def main():
    data = smartsheet.extract_data(SHEET_ID)
    dynamodb.update_table(SHEET_ID, data)


# AWS Lambda Function
def handler(event, context):
    main()
    return {"statusCode": 200}


if __name__ == "__main__":
    enable_logging_to_console(logging.INFO)
    test_smartsheet_connection()
    sheet, data, table = main()
