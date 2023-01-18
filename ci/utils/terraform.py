import dagger

from utils.misc import find_repo_path

# TODO: Dynamically configure the build container, i.e only use .with_unix_socket when
# its actually appropriate...
def configure_build_env(client: dagger.Client, tf_workdir: str) -> dagger.Container:
    """Configure and returns a build container.
    :param client: The dagger client.
    :param tf_workdir: The Terraform working directory which will be mounted to the
        build container.
    :return: The build container.
    :rtype: dagger.Container
    """

    # find the root repo path
    repo_root = find_repo_path()

    # path where the Dockerfile dagger runners are located
    Dockerfiles_dir = client.host().directory(path=f"{repo_root}/ci/Dockerfiles")

    # configure the secrets for the build container
    aws_access_key_id = client.host().env_variable("AWS_ACCESS_KEY_ID").secret()
    aws_secret_access_key = client.host().env_variable("AWS_SECRET_ACCESS_KEY").secret()
    aws_session_token = client.host().env_variable("AWS_SESSION_TOKEN").secret()

    # path where the terraform configuration files are located
    terraform_dir = client.host().directory(path=tf_workdir)

    # to run docker in docker, we need to connect to the docker socket.
    docker_host = client.host().unix_socket("/var/run/docker.sock")

    # lets use the Terraform Dockerfile located under Dockerfiles/ just to showcase the example
    # if you wanted to use the docker image packaged to this repo, you would do something like
    # .from_("ghcr.io/gonzalezandrew/dagger-tf-example:main")
    return (
        client.container()
        .build(context=Dockerfiles_dir, dockerfile="Dockerfile_tf_runner")
        .with_secret_variable("AWS_ACCESS_KEY_ID", aws_access_key_id)
        .with_secret_variable("AWS_SECRET_ACCESS_KEY", aws_secret_access_key)
        .with_secret_variable("AWS_SESSION_TOKEN", aws_session_token)
        .with_unix_socket("/var/run/docker.sock", docker_host)
        .with_mounted_directory("/src", terraform_dir)
        .with_workdir("/src")
    )


def terraform_commands():
    """Configure and return a map of Terraform commands.
    :return: A map of Terraform commands
    :rtype: dict[str, list[str]]
    """

    # global commands that are used by most tf commands
    # this is a personal choice and you can get rid of this!
    global_commands = [
        "-input=false",
        "-refresh=true",
    ]

    # TODO: plan-txt command is UGLY, make it cute
    terraform_commands = {
        "plan": ["terraform", "plan"],
        "apply": ["terraform", "apply", "-auto-approve"],
        "init": ["terraform", "init"],
        "destroy": ["terraform", "apply", "-destroy", "-auto-approve"],
        "plan-destroy": ["terraform", "plan", "-destroy"],
        "update": ["terraform", "get", "-update=true"],
        "plan-txt": ["terraform", "plan", "-no-color"],
    }

    for command_name, args in terraform_commands.items():
        # if any of these commands are here, lets append the global args to them
        if any(map(command_name.__contains__, ["apply", "plan", "destroy"])):
            terraform_commands[command_name].extend(global_commands)

        # for plan-txt, we have to send the output to a file using redirection
        if "plan-txt" in command_name:
            terraform_commands[command_name].append("> tfplan.txt")

    return terraform_commands
