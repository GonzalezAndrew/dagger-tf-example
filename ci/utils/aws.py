import os

import boto3


def get_aws_creds(profile: str = None):
    """Get AWS credentials using boto3"""
    if profile is None:
        profile = os.environ.get("AWS_PROFILE")
    else:
        raise ValueError(
            "Please set the arg `profile` or set the AWS_PROFILE environment variable."
        )

    if os.environ.get("AWS_ACCESS_KEY_ID") is None:
        print("Getting AWS credentials from boto and the local aws config file.")
        try:
            session = boto3.Session(profile_name=profile)
            credentials = session.get_credentials()

            os.environ["AWS_ACCESS_KEY_ID"] = credentials.access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = credentials.secret_key
            os.environ["AWS_SESSION_TOKEN"] = credentials.token
        except Exception as e:
            raise e

    else:
        print(
            "Looks like we already have AWS creds set, skipping generation new credentials."
        )
