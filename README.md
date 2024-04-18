
# Welcome to your CDK Python project!

This is your CDK-based deployment project for the [fast_api_jwt](https://github.com/tangledpath/cdk-fast-api-jwt) app.  It works by using CDK IaC to create deployment stacks using code from that project, by virtue of its being in a known relative directory.  We will also have other projects associated with this stack, so it makes sense to have a dedicated master project to create comprehensive stack which will include the lambda handler, the fastapi service, a user interface and additional services.      

The `cdk.json` file tells the CDK Toolkit how to execute your app.  This app is poetry-based for your convenience.  If you don't have poetry, install it.

To get started in your poetry environment
```bash
poetry install --no-root
poetry shell
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to the [pyproject.toml](pyproject.toml) file and run the `poetry update`
command.  Instead of editing [pyproject.toml](pyproject.toml), you can also add dependencies using `poetry add <package_name>`.  For example, to install [python-dotenv](https://pypi.org/project/python-dotenv/), use the command: `poetry add python-dotenv` 

## Useful commands
 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
