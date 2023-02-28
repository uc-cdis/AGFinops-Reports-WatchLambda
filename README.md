# AGFinops-Reports-WatchLambda
Lambda function to watch opencost reports submitted to OCC

## Watch the Lambda function

The watch lambda function keeps a watch on opencost reports submitted to OCC in opencost-report-bucket. The code contains the methods to read the file uploaded to s3, and check if any data is available. If data is not available then the code will send a slack notification to channel #opecost-lambda-alert


The lambda_function is called when any new object is uploaded into the s3 bucket.

### ENV Variables

* SLACK_CHANNEL - The name of the slack channel in which the lambda alert would generate. e.g. #opencost-lambda-alert
* SLACK_WEBHOOK_URL - The webhook URL to the slack channel mentioned above. e.g. https://hooks.slack.com/services/XX8SXX/XXXXXxxxxxxxefesdvsdvsvdvdvdv
