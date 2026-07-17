import boto3
import io
import os
import re
import requests
from botocore.config import Config
from subprocess import run, PIPE
from flask import Flask
from flask_restful import Resource, Api, reqparse
from threading import Thread
from uuid import uuid4
from tempfile import mkdtemp

# Never put credentials in your code!
from dotenv import load_dotenv
load_dotenv()


B2_REGION_PATTERN = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}$')


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f'{name} is required (see .env.example)')
    return value


def validated_b2_region():
    region = required_env('B2_REGION')
    if not B2_REGION_PATTERN.fullmatch(region):
        raise SystemExit(
            'B2_REGION must be a Backblaze region token like us-west-001 '
            '(see .env.example)'
        )
    return region


# Obtain B2 S3 compatible client
B2_REGION = validated_b2_region()

s3 = boto3.client(service_name='s3',
                  endpoint_url=f'https://s3.{B2_REGION}.backblazeb2.com',
                  region_name=B2_REGION,
                  aws_access_key_id=required_env('B2_APPLICATION_KEY_ID'),
                  aws_secret_access_key=required_env('B2_APPLICATION_KEY'),
                  config=Config(
                      user_agent_extra='b2-transcoder-worker (backblaze-b2-samples)'
                  ))

bucket_name = required_env('B2_BUCKET_NAME')

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('inputObject', required=True)
parser.add_argument('webhook', required=True)


def transcode(inputObject, webhook):
    input_key = inputObject

    # Unfortunately, we can't stream the B2 object into ffmpeg, since many video
    # formats require ffmpeg to seek around the data to decode it
    input_file = os.path.join(mkdtemp(), str(uuid4()))

    print(f'Downloading s3://{bucket_name}/{input_key} to {input_file}')

    s3.download_file(bucket_name, input_key, input_file)

    output_file = input_file + '.mp4'
    command = f'ffmpeg -i {input_file} -c:a copy -s hd720 -preset superfast -y {output_file}'

    print(f'Running {command}', flush=True)

    # Have to run in a shell to make this work in a worker thread
    cp = run(command, shell=True)

    print(f'Exit status {cp.returncode}')

    if cp.returncode == 0:
        output_key = os.path.splitext(input_key)[0]+'.mp4'

        print(f'Uploading {output_file} to s3://{bucket_name}/{output_key}')
        s3.upload_file(output_file, bucket_name, output_key)

        response = {
            'status': 'success',
            'inputObject': input_key,
            'outputObject': output_key
        }
    else:
        response = {
            'status': 'failure',
            'inputObject': input_key
        }

    print(f'POSTing {response} to {webhook}')
    r = requests.post(webhook, json=response)
    print(f'Status code {r.status_code}')


class Videos(Resource):
    def post(self):
        args = parser.parse_args()
        thread = Thread(target=transcode, kwargs={**args})
        thread.start()
        return {'status': 'transcoding'}, 200


api.add_resource(Videos, '/videos')

if __name__ == '__main__':
    app.run()
