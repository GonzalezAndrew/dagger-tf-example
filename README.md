# Dagger Terraform Example

Here is a rough POC I did using dagger to deploy our AWS lambdas that are all container images. I followed what everyone did and just wrapped a pipeline in a CLI and added some other arguments to the help in deploying infra with Terraform. An ugly thing I had to do was add the argument `local` which I use to help distinguish between when I'm running dagger in a CI/CD environment and on my local machine. When authenticating to AWS, I authenticate differently than my CI/CD environment so the `local` argument handles the logic behind the different authentication methods used. I'm sure this can be improved on and I will investigate further later. 


```
python3 ci/main.py tf-deploy --help
usage: dagger tf-deploy [-h] [--workdir WORKDIR] [--environment ENVIRONMENT] [--output-commands] [--dry-run]
                        [--local] [--profile PROFILE]

options:
  -h, --help            show this help message and exit
  --workdir WORKDIR     The working directory where the Terraform configuration files will be located.
  --environment ENVIRONMENT
                        The environment we are deploying to. This also tells the pipeline which inputs.tfvars and
                        backend.hcl we are using for the deployment.
  --output-commands     Output all possible predefined terraform commands.
  --dry-run             Dry run the given pipeline. There will be no changes to the infrastructure. This is a
                        simple terraform init and plan. The plan will be output to the stdout.
  --local               When you are running the pipeline on your local machine. This is used to pass AWS
                        credentials from your local machine to the Dagger build container. You will need to
                        authenticate to AWS with sso and set the environment variable `AWS_PROFILE` in order to
                        run the pipeline on your local machine properly.
  --profile PROFILE     Passing a AWS profile to the pipeline. This is usually only used when you're running
                        dagger on your local machine and you do not wish to set the `AWS_PROFILE` environment
                        variable.

```

Here is an example of using the dagger pipeline to deploy to production on our local machine.
```
$ python3 ci/main.py tf-deploy --workdir=aws_lambda_1 --environment=production --local
```

Using a CI/CD provider, the pipeline can be used to run multiple deployments at a given time. For example using Circle CI matrix jobs, we can do something like so:

```yaml
version: 2.1

commands:
  aws-oidc-setup:
    description: Setup AWS auth using OIDC token
    parameters:
      aws-role-arn:
        type: string
    steps:
      - run:
          name: Get short-term credentials
          command: |
            echo << parameters.aws-role-arn >>
            STS=($(aws sts assume-role-with-web-identity --role-arn << parameters.aws-role-arn >> --role-session-name "${CIRCLE_BRANCH}-${CIRCLE_BUILD_NUM}" --web-identity-token "${CIRCLE_OIDC_TOKEN}" --duration-seconds 900 --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text))
            echo "export AWS_ACCESS_KEY_ID=${STS[0]}" >> $BASH_ENV
            echo "export AWS_SECRET_ACCESS_KEY=${STS[1]}" >> $BASH_ENV
            echo "export AWS_SESSION_TOKEN=${STS[2]}" >> $BASH_ENV
            echo "export AWS_REGION=us-east-1" >> $BASH_ENV

  run_dagger:
    description: Run dagger pipeline
    parameters:
      dagger_pipeline:
        type: string
        description: The dagger pipeline to run
    steps:
      - run:
          name: Install deps
          command: |
            python3.10 -m pip install --upgrade pip
            if [ -f ci/requirements.txt ]; then python3.10 -m pip install -r ci/requirements.txt; fi
            python3.10 -m pip install dagger-io
      - run:
          name: Run Dagger << parameters.dagger_pipeline >>
          command: |
            python3.10 ci/main.py << parameters.dagger_pipeline >>

jobs:

  update-lambdas:
    parameters:
      aws-role-arn:
        type: string
      dagger_pipeline:
        type: string
    machine:
      image: ubuntu-2204:2022.10.1
      docker_layer_caching: true
    steps:
      - checkout
      - aws-oidc-setup:
          aws-role-arn: << parameters.aws-role-arn >>
      - run_dagger:
          dagger_pipeline: << parameters.dagger_pipeline >>

workflows:
  update_all_lambdas:
    jobs:
      - update-lambdas:
          name: update-staging-lambdas
          context: my-context
          aws-role-arn: "arn:aws:iam::1101010101011:role/my-staging-role"
          matrix:
            parameters:
              dagger_pipeline:
                [
                  "tf-deploy --workdir=aws_lambda_1 --environment=staging",
                  "tf-deploy --workdir=aws_lambda_2 --environment=staging",
                  "tf-deploy --workdir=aws_lambda_3 --environment=staging",
                ]

      - update-lambdas:
          name: dry-run-prod-us-east-1-lambdas
          context: my-context
          aws-role-arn: "arn:aws:iam::0101010101010:role/my-prod-role"
          matrix:
            parameters:
              dagger_pipeline:
                [
                  "tf-deploy --workdir=aws_lambda_1 --environment=production --dry-run",
                  "tf-deploy --workdir=aws_lambda_2 --environment=production --dry-run",
                  "tf-deploy --workdir=aws_lambda_3 --environment=production --dry-run",
                ]

```
