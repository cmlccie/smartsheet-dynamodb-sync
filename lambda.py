#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""SmartSheet-to-DynamoDB Sync Lambda Function."""


# Add vendor directory to module search path
import os
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.append(vendor_dir)

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import logging
import sys
from base64 import b64decode

import boto3

import ssdbsync


__author__ = "Chris Lunsford"
__author_email__ = "chrlunsf@cisco.com"
__copyright__ = "Copyright (c) 2017 Cisco Systems, Inc."
__license__ = "MIT"


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


# AWS Lambda Function Handler
def handler(event, context):
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)
        return {"statusCode": 500}
    else:
        return {"statusCode": 200}


# Running the script on a developer workstation
if __name__ == "__main__":
    ssdbsync.enable_console_logging()
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)
        sys.exit(1)
    else:
        sys.exit(0)
