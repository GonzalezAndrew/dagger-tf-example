"""
Create a simple pipeline for a deploying a Lambda function.
"""

import os
import sys

import anyio
import dagger
import graphql


def build_image(client: dagger.Client):
    """ Returns a build environment to be used by a Terraform project.
    :param client: The dagger Client object.
    :return: A dagger Container object.
    :rtype: dagger.Container
    """
    # get reference to the local project
    src = client.host().directory(".")

    # configure the secrets for the build container
    aws_access_key_id = client.host().env_variable("AWS_ACCESS_KEY_ID").secret()
    aws_secret_access_key = client.host().env_variable("AWS_SECRET_ACCESS_KEY").secret()
    aws_session_token = client.host().env_variable("AWS_SESSION_TOKEN").secret()
    aws_region = os.getenv("AWS_REGION", "us-east-1")

    # to run docker in docker, we need to connect to the docker socket.
    docker_host = client.host().unix_socket("/var/run/docker.sock")

    return (
        client.container()
        .from_("ghcr.io/gonzalezandrew/dagger-tf-example:main")
        .with_env_variable("AWS_REGION", aws_region)
        .with_secret_variable("AWS_ACCESS_KEY_ID", aws_access_key_id)
        .with_secret_variable("AWS_SECRET_ACCESS_KEY", aws_secret_access_key)
        .with_secret_variable("AWS_SESSION_TOKEN", aws_session_token)
        .with_unix_socket("/var/run/docker.sock", docker_host)
        .with_mounted_directory("/src", src)
        .with_workdir("/src")
    )


def init(image: dagger.Container):
    pass

def plan(image: dagger.Container):
    pass

def apply(image: dagger.Container):
    pass

async def main():
    """main"""
    # initialize dagger client
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        # lets grab the build environment
        build = build_image(client=client)
        
        await build.exec(["terraform", "-version"]).stdout()

if __name__ == "__main__":
    try:
        anyio.run(main)
    except graphql.GraphQLError as e:
        print(e.message, file=sys.stderr)
        sys.exit(1)