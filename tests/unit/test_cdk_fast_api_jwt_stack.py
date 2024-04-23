import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_fast_api_jwt.cdk_fast_api_jwt_stack import CdkFastApiJwtStack
from app import MultistackApp

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_fast_api_jwt/cdk_fast_api_jwt_stack.py
def test_sqs_queue_created():
    app = MultistackApp()
    stacks = app.create_stacks(environments=['test'])
    stack = stacks['test']
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties('AWS::SQS::Queue', {
        'VisibilityTimeout': 360,
        'QueueName': 'test-tapestryworlds-sqs-sqs_queue.fifo',
    })

    template.has_resource_properties('AWS::S3::Bucket', {
        'BucketName': 'test-tapestryworlds-s3-images-bucket',
    })

    template.has_resource_properties('AWS::Lambda::Function', {
        'FunctionName': 'test-lambda-command-fn',
    })
