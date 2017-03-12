init: requirements.txt vendor.txt
	pip install -r requirements.txt
	pip install -t vendor -r vendor.txt

zip: smartsheet-dynamodb-sync.py
	zip -r smartsheet-dynamodb-sync.zip smartsheet-dynamodb-sync.py vendor/*
