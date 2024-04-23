#!/usr/bin/service_env python3
import copy
from typing import Dict, Any, Sequence

import aws_cdk as cdk
from dotenv import dotenv_values

from cdk_fast_api_jwt.cdk_fast_api_jwt_stack import CdkFastApiJwtStack, StackConfig


class MultistackApp:
    # Name for our production stack.  Staging/dev/other stacks will prepend a prefix:
    STACK_NAME_BASE = "CdkFastApiJwtStack"

    """
    Base stack configuration.  The actual stack stack_config used to build
    the stack may add prefixes, and additional runtime environment variables.
    If additional services or configuration is needed, add it here, and make
    use of it in the stack itself.  For example, our environment for the
    lambda function and the fargate service.  If we end up needing different
    environments instead, we'd add the second one here, then reference that one
    when creating the associated service in the stack code.
    """
    STACK_CONFIG_BASE = StackConfig(
        service_env=dotenv_values(".env"),
        fargate_service_name="tapestryworlds-service",
        lambda_fn_name="lambda-command-fn",
        sqs_queue_name="tapestryworlds-sqs-sqs_queue.fifo",
        s3_bucket_name="tapestryworlds-s3-images-bucket",
    )

    def __init__(self):
        """ Constructor for our multistack app """
        self.cdk_app = cdk.App()

    def create_stacks(self, environments: Sequence[str] = ['production', 'staging', 'test']):
        """
            Called to create the stacks for this app.  The CDK CLI will allow
            the user to create one, several, or all stacks available:

            :param environments: List of environments to create; default is ['production', 'staging', 'test']
        """
        stack_env = dict()
        stacks = {}
        if 'production' in environments:
            stacks['production'] = self.__create_stack(environment='production', stack_env=stack_env)
        elif 'staging' in environments:
            stacks['staging'] = self.__create_stack(environment='staging', stack_env=stack_env)
        elif 'test' in environments:
            stacks['test'] = self.__create_stack(environment='test', stack_env=stack_env)

        return stacks

    def __create_stack(self, environment: str, stack_env: Dict[str, Any]):
        """
        Create a specific stack based on given environment name @public
        :param environment: will be used as a prefix (delimited by a dash)
            for the stack name.  It will also be used as a prefix for the name
            values in `STACK_CONFIG_BASE`.  Note: in the case where environment
            is 'production', there will be no prefix applied.
            `service_env.APP_ENV` will also be set to `environment`, so the code
            running in the various AWS services can easily determine which under
            which environment its stack is running.

        :param stack_env: Environment variables to be used when building the stack
             on AWS.  This is useful if you want to deploy with a different account
             and/or to a different region.  Example keys: `account`,
             `region`.
        """
        stack_config = copy.deepcopy(self.STACK_CONFIG_BASE)
        if environment == 'production':
            stack_name = self.STACK_NAME_BASE
        else:
            stack_name = f"{environment.capitalize()}{self.STACK_NAME_BASE}"
            stack_config.fargate_service_name = f"{environment}-{stack_config.fargate_service_name}"
            stack_config.lambda_fn_name = f"{environment}-{stack_config.lambda_fn_name}"
            stack_config.sqs_queue_name = f"{environment}-{stack_config.sqs_queue_name}"
            stack_config.s3_bucket_name = f"{environment}-{stack_config.s3_bucket_name}"
            stack_config.service_env.APP_ENV = environment
            stack_config.service_env.S3_BUCKET_NAME = stack_config.s3_bucket_name
            stack_config.service_env.SQS_QUEUE_NAME = stack_config.sqs_queue_name

        return CdkFastApiJwtStack(
            scope=self.cdk_app,
            construct_id=stack_name,
            stack_config=stack_config,
            stack_name=stack_name,
            env=stack_env,
        )


if __name__ == "__main__":
    # Create instance of our app; then create the stacks:
    app = MultistackApp()
    app.create_stacks()
    app.cdk_app.synth()
