import os
import requests
import boto3
import botocore.exceptions

USER_POOL_REGION = os.getenv('USER_POOL_REGION')
USER_POOL_ID = os.getenv('USER_POOL_ID')
API_BASE_URL = 'http://localhost:5000'
ADMIN_USERID = ''

def cognito_list_groups():
    client = boto3.client('cognito-idp', region_name=USER_POOL_REGION)
    try:
        resp = client.list_groups(UserPoolId = USER_POOL_ID,)
    except Exception as e:
        return None, e.__str__()
    return resp, None

def import_workspaces():
    res, err = cognito_list_groups()
    #print(res, err)
    if res:
        for g in res['Groups']:
            data = {
                'name': g['GroupName'],
                'description': g['Description'],
            }
            #headers = {
            #    'x-omic-userid': ADMIN_USERID
            #}
            try:
                response = requests.post(
                    f'{API_BASE_URL}/workspace',
                    data=data,
                    #headers=headers
                )
                print(response.json())
            except requests.exceptions.HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
            except Exception as err:
                print(f'Other error occurred: {err}')

if __name__ == '__main__':
  import_workspaces()