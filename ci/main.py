import argparse
import sys

from pipeline.tf_deploy import tf_deploy


def _add_shared_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Dry run the given pipeline. There will be no changes to the infrastructure. "
            "This is a simple terraform init and plan. The plan will be output to the stdout. "
        ),
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help=(
            "When you are running the pipeline on your local machine. "
            "This is used to pass AWS credentials from your local machine "
            "to the Dagger build container. You will need to authenticate to "
            "AWS with sso and set the environment variable `AWS_PROFILE` in order "
            "to run the pipeline on your local machine properly. "
        ),
    )

    parser.add_argument(
        "--profile",
        help=(
            "Passing a AWS profile to the pipeline. "
            "This is usually only used when you're running dagger on your local machine "
            "and you do not wish to set the `AWS_PROFILE` environment variable. "
        ),
    )


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="dagger",
        description="A command line tool to run dagger pipelines.",
    )

    subparser = parser.add_subparsers(dest="command")

    tf_deploy_parser = subparser.add_parser(
        "tf-deploy", help="Deploys the given Terraform config."
    )
    tf_deploy_parser.add_argument(
        "--workdir",
        help="The working directory where the Terraform configuration files will be located.",
    )
    tf_deploy_parser.add_argument("--environment", default="staging", help=(
            "The environment we are deploying to. "
            "This also tells the pipeline which inputs.tfvars and backend.hcl we are using for the deployment. "
        )
    )
    
    tf_deploy_parser.add_argument(
        "--output-commands",
        action="store_true",
        help=("Output all possible predefined terraform commands."),
    )

    _add_shared_option(tf_deploy_parser)

    help = subparser.add_parser("help", help="Show the help for a specific command.")
    help.add_argument("help_cmd", nargs="?", help="Command to show help for.")

    if len(argv) == 0:
        parser.print_help()

    args = parser.parse_args(argv)
    if args.command == "help" and args.help_cmd:
        parser.parse_args([args.help_cmd, "--help"])
        return 0
    elif args.command == "help":
        parser.parse_args(["--help"])
        return 0

    if args.command == "tf-deploy":
        tf_deploy(args)
    else:
        raise NotImplementedError(f"The command {args.command} is not implemented!")


if __name__ == "__main__":
    raise SystemExit(main())
