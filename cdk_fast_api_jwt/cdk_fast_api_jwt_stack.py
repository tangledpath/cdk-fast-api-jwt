from dataclasses import dataclass
from typing import Dict

from aws_cdk import (
    aws_ecs as ecs,
    aws_ecr_assets as ecr_assets,
    aws_ecs_patterns as ecs_patterns,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_event_sources,
    CfnOutput, Duration, RemovalPolicy, Stack,
)
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_ecs_patterns import ApplicationLoadBalancedFargateService
from aws_cdk.aws_lambda import DockerImageFunction, Function
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket as S3Bucket
from aws_cdk.aws_sqs import Queue as SQSQueue
from constructs import Construct


@dataclass
class StackConfig:
    """ Configuration items for stack"""
    service_env: Dict[str, str]
    fargate_service_name: str
    lambda_fn_name: str
    s3_bucket_name: str
    sqs_queue_name: str


class CdkFastApiJwtStack(Stack):
    """ Our CDK Stack for FastAPI JWT.  Use parameters of constructor to control """

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            stack_config: StackConfig,
            **kwargs
    ) -> None:
        """
        Constructor for CdkFastApiJwtStack.  The stack is fully built here.
        :param scope: Our overall CDK Application
        :param construct_id: Identifier for this stack
        :param env: Dictionary of environment to use for the lambda fn as well as the service
        :param lambda_fn_name: Name of the lambda function
        :param s3_bucket_name: Name for the S3 bucket
        :param fargate_service_name: Name for the Fargate service
        :param sqs_queue_name: Name for the SQS Queue
        :param kwargs: Other kwargs passed to Stack base class
        """
        super().__init__(scope, construct_id, **kwargs)
        self.config = stack_config

        # Create our SQS sqs_queue
        self.sqs_queue = self.__create_sqs_queue()

        # Create the S3 bucket:
        self.s3_bucket = self.__create_s3_bucket()

        # Create the fargate service:
        self.fargate_service = self.__create_fargate_service("../fast-api-jwt")

        # Create the lambda lambda_fn:
        self.lambda_fn = self.__create_lambda("../fast-api-jwt")

        # Add SQS event source to the Lambda lambda_fn
        self.lambda_fn.add_event_source(lambda_event_sources.SqsEventSource(self.sqs_queue))

        self.__express_output()

    def __create_lambda(self, directory: str) -> Function:
        """
        Create lambda from a Dockerfile and return it
        :param directory: Directory containing Dockerfile
        """

        # Create a lambda docker asset from the Dockerfile
        lambda_docker_image = _lambda.DockerImageCode.from_image_asset(
            directory=directory,
            file='Dockerfile.lambda.handler',
            platform=Platform.LINUX_AMD64,
        )
        # Create a Lambda lambda_fn from the Docker image
        function = DockerImageFunction(
            scope=self,
            id=self.config.lambda_fn_name,
            code=lambda_docker_image,
            environment=self.config.service_env,
            function_name=self.config.lambda_fn_name,
            description='Lambda to execute commands (modifications to the database)',
            timeout=Duration.seconds(300),
        )
        return function

    def __create_fargate_service(self, directory) -> ApplicationLoadBalancedFargateService:
        # Create an ECR docker asset from the Dockerfile
        service_docker_image = ecr_assets.DockerImageAsset(
            scope=self,
            id="FastAPIImage",
            directory=directory,
            file='Dockerfile.fargate.service',
            platform=Platform.LINUX_AMD64,
        )
        # Create a Fargate service
        fargate_service = ApplicationLoadBalancedFargateService(
            scope=self,
            id=self.config.fargate_service_name,
            service_name=self.config.fargate_service_name,
            public_load_balancer=True,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_docker_image_asset(service_docker_image),
                container_port=8080,
                environment=self.config.service_env
            ),
        )
        return fargate_service

    def __create_s3_bucket(self) -> S3Bucket:
        """ Create an S3 bucket w/public_read_access using `self.config.s3_bucket_name """
        s3_bucket = S3Bucket(
            scope=self,
            id=self.config.s3_bucket_name,
            bucket_name=self.config.s3_bucket_name,
            public_read_access=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            )
        )
        return s3_bucket

    def __create_sqs_queue(self) -> SQSQueue:
        """ Create and return new SQS Queue named sqs_queue_name """
        queue = SQSQueue(
            scope=self,
            id=self.config.sqs_queue_name,
            queue_name=self.config.sqs_queue_name,
            fifo=True,
            visibility_timeout=Duration.seconds(300),
        )
        return queue

    def __express_output(self):
        """ Create/display output for this stack. """
        CfnOutput(
            self, 'S3BucketName',
            value=self.s3_bucket.bucket_name,
            description='S3 Bucket Name',
        )
        CfnOutput(
            self, 'FargateServiceName',
            value=self.fargate_service.service.service_name,
            description='Fargate Service Name',
        )
        CfnOutput(
            self, 'LambdaFunctionName',
            value=self.lambda_fn.function_name,
            description='Lambda lambda_fn name',
        )
        CfnOutput(
            self, 'SQSqueueName',
            value=self.sqs_queue.queue_name,
            description='SQS sqs_queue name',
        )
        CfnOutput(
            self, 'SQSqueueARN',
            value=self.sqs_queue.queue_arn,
            description='SQS sqs_queue ARN',
        )
        CfnOutput(
            self, 'SQSqueueURL',
            value=self.sqs_queue.queue_url,
            description='SQS sqs_queue URL',
        )
