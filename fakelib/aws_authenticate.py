import os
import subprocess
import json

def _system(cmd):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    stupidBytesObject = proc_stdout
    outStr = (stupidBytesObject.decode("utf-8"))
    #print(outStr)
    return(outStr)

def _set_aws_credential_env(json_in):
    data = json.loads(json_in)
    key = data['Credentials']['AccessKeyId']
    secret = data['Credentials']['SecretAccessKey']
    session_token = data['Credentials']['SessionToken']

    os.environ['AWS_ACCESS_KEY_ID'] = key
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret
    os.environ['AWS_SESSION_TOKEN'] = session_token

    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    os.environ['AWS_REQUEST_PAYER'] = 'requester'


def aws_authenticate():
    AWS_STS_RESPONSE='aws sts assume-role-with-web-identity --role-arn arn:aws:iam::376067480372:role/eks-pangeo-node --role-session-name gdal-session-$(date +%s) --web-identity-token file:///var/run/secrets/eks.amazonaws.com/serviceaccount/token'

    output = _system(AWS_STS_RESPONSE)
    #print(output)
    _set_aws_credential_env(json_in=output)
