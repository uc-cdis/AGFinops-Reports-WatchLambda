import json
import pandas as pd
import requests
import urllib.parse
import boto3
import os
from datetime import datetime

s3 = boto3.client("s3")

## This lambda would trigger when an entry is made to s3 bucket named opencost-report-bucket


def lambda_handler(event, context):

    # Get Bucket name and key name of the new file uploaded on s3
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        send_exception(
            "Error getting object *"
            + key
            + "* from bucket *"
            + bucket
            + "* . Make sure they exist and your bucket is in the same region as this function."
            + ". error: "
            + str(e)
        )
    parse_file_content(bucket, key)
    return response["ContentType"]


# parse file content of the new file uploaded on s3
def parse_file_content(s3_bucket, s3_file_name):

    s3_json_object = s3.get_object(Bucket=s3_bucket, Key=s3_file_name)
    s3_object_url = "https://{}.s3.amazonaws.com/{}".format(s3_bucket, s3_file_name)

    # Check if Body Exsist in the the s3 object
    if "Body" not in s3_json_object:
        send_exception(
            "The s3 file could not be read *" + s3_file_name + "*", s3_object_url
        )

    # Read file Content of the file
    file_content = json.loads(s3_json_object["Body"].read())

    # Skip All Content which are empty
    file_content_array = [i for i in file_content["data"] if len(i) > 0]

    if len(file_content_array) > 0:
        for file_content in file_content_array:
            for k, v in file_content.items():
                if k == "" or len(v) <= 0:
                    send_exception(
                        "The s3 file " + s3_file_name + " have missing data",
                        s3_object_url,
                    )
        print("File Has Content")
    else:
        send_exception(
            "The s3 file *" + s3_file_name + "* do not have any data", s3_object_url
        )


# Send Slack notification
def send_exception(message="", s3_object_url=""):
    data = {
        "text": "Notification!",
        "blocks": slack_data(message, s3_object_url),
        "channel": os.environ["SLACK_CHANNEL"],
        "username": "webhookbot",
    }
    print(data)

    print(json.dumps(data))

    response = requests.post(
        os.environ["SLACK_WEBHOOK_URL"],
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )

    if response.status_code != 200:
        raise ValueError(
            "Request to slack returned an error %s, the response is:\n%s"
            % (response.status_code, response.text)
        )


# Body of the slack notification
def slack_data(message, s3_object_url):
    _message = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": "Opencost Report notification :warning:",
                "emoji": True,
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n>*Trigger*\n>Error for Opencost Report File: \n>" + message,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "emoji": True,
                }
            ],
        },
    ]
    if s3_object_url:
        _message[2]["accessory"] = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "Link to S3 Object",
                "emoji": True,
            },
            "value": "click_me_123",
            "url": s3_object_url,
        }

    return _message
