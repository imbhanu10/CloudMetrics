
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
        sns = boto3.client('sns')
        arn = 'arn of your AWS SNS'  # Your arn should be the arn of the particular SNS Service
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        notification = f'cloudmetrics: System report logs have been uploaded into your S3 bucket ({bucket_name})'

        response = sns.publish(
            TargetArn = arn,
            Message = json.dumps({'default': notification}),
            MessageStructure = 'json'
            )

        # log to AWS CloudWatch
        logger.info('Function {} has executed.'.format(context.function_name))

        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
