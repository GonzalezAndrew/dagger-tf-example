import argparse
import sys

import anyio
import asyncer
import dagger

from utils.terraform import configure_build_env
from utils.terraform import terraform_commands

from utils.aws import get_aws_creds

from rich.console import Console
from rich.table import Table


def __output(data: dict) -> None:
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Command Name", justify="left")
    table.add_column("Actual Terraform Command")

    for key, value in data.items():
        table.add_row(str(key), f"[bold]{value}[bold]")

    console.print(table)


async def run_pipeline(tf_workdir: str, dry_run: bool):
    """Run the pipeline"""
    async with dagger.Connection(
        dagger.Config(log_output=sys.stderr, timeout=60000, execute_timeout=3000)
    ) as client:

        # lets get a map of predefined terraform commands to help us
        # easily run terraform commands
        commands = terraform_commands()

        # the dagger build container obj
        builder = configure_build_env(client, tf_workdir)

        # lets add tf init and plan to the build container
        terraform_plan = builder.exec(commands["init"]).exec(commands["plan"])

        # if we are running in dry mode just output tf plan
        if dry_run:
            await terraform_plan.stdout()
        else:
            # if we are deploying, append the tf apply command to the build container
            # and await the container to finish the apply
            terraform_apply = await (terraform_plan.exec(commands["apply"])).stdout()


def tf_deploy(args: argparse.Namespace):
    """Run a full Terraform workflow"""
    # output the predefined tf commands
    if args.output_commands:
        commands = terraform_commands()
        __output(commands)
        return 0

    # the terraform work dir
    workdir = args.workdir

    # run the tf-deploy pipeline in dry mode
    dry_run = args.dry_run

    # if we are running locally, grab the aws creds
    if args.local:
        get_aws_creds(args.profile)

    try:
        asyncer.runnify(run_pipeline)(tf_workdir=workdir, dry_run=dry_run)
    except Exception as e:
        raise e
