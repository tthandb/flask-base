import os
from git import Repo
import subprocess
import json
import boto3
from common.helpers.aws_cli import print_success, aws_cli
from urllib.request import Request, urlopen


class S3Client:
    def __init__(self):
        self.s3 = boto3.resource('s3')
        self.s3_client = boto3.client('s3')

    def _all(self):
        result = []
        for bucket in self.s3.buckets.all():
            result.append(bucket.name)
        return result

    def _delete(self, name):
        if name is None or name == '':
            raise Exception('Bucket Name is required')

        self.s3_client.delete_objects(Bucket=name)
        return True

    def _delete_all(self):
        for bucket in self.s3.buckets.all():
            bucket = self.s3.Bucket(bucket.name)
            bucket.objects.all().delete()
            self.s3_client.delete_bucket(Bucket=bucket.name)
            print_success('Deleted bucket: {}'.format(bucket.name))

    def _create(self, name, region='ap-southeast-1'):
        if name is None or name == '':
            raise Exception('Bucket Name is required')

        response = self.s3_client.create_bucket(
            ACL='public-read',
            Bucket=name,
            CreateBucketConfiguration={
                'LocationConstraint': region
            },
        )
        return response

    def _set_website(self, name):
        if name is None or name == '':
            raise Exception('Bucket Name is required')

        response = self.s3_client.put_bucket_website(
            Bucket=name,
            WebsiteConfiguration={
                'ErrorDocument': {
                    'Key': 'error.html'
                },
                'IndexDocument': {
                    'Suffix': 'index.html'
                }
            }
        )
        return response

    def _put_policy(self, name):
        if name is None or name == '':
            raise Exception('Bucket Name is required')

        self.s3_client.put_bucket_policy(
            Bucket=name,
            Policy=json.dumps({
                'Version': '2012-10-17',
                'Statement': [{
                    'Sid': 'PublicReadGetObject',
                    'Effect': 'Allow',
                    'Principal': '*',
                    'Action': [
                        's3:GetObject'
                    ],
                    'Resource': [
                        'arn:aws:s3:::{}/*'.format(name)
                    ]
                }]
            })
        )
        return True

    def sync(self, name, cella_info):
        if name is None or name == '':
            raise Exception('Bucket Name is required')

        local_folder = './temp/{}'.format(name)
        self.__build_data(cella_info, local_folder)
        result = aws_cli(
            's3',
            'sync',
            '{}/dist/'.format(local_folder),
            's3://{}'.format(name),
            '--acl',
            'public-read',
            '--delete'
        )
        return result