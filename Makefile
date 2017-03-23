init: requirements.txt vendor.txt
	pip install -r requirements.txt
	pip install -t vendor -r vendor.txt

lambda-zip: lambda.py
	zip -r build/ssdb-sync_lambda_function.zip lambda.py LICENSE.txt vendor/*

aws-s3-bucket:
	aws s3 mb s3://ssdb-sync

aws-cloudformation-deployment: samTemplate.yaml
	aws cloudformation package \
		--template-file samTemplate.yaml \
		--output-template-file build/serverless-output.yaml \
		--s3-bucket ssdb-sync

	aws cloudformation deploy \
		--template-file build/serverless-output.yaml \
		--stack-name ssdb-sync \
		--capabilities CAPABILITY_IAM
