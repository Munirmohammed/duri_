import boto3


def get_services(access_key, secret_key, session_token=None):
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        aws_session_token=session_token
    )
    available_services = session.get_available_services()
    return available_services


def assume_role(external_id, role_arn):
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='AssumedSession',
        ExternalId=external_id
    )
    credentials = response['Credentials']
    access_key_id = credentials['AccessKeyId']
    secret_access_key = credentials['SecretAccessKey']
    session_token = credentials['SessionToken']
    return access_key_id, secret_access_key, session_token
