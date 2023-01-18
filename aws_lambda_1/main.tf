provider "aws" {
  region = "us-east-1"
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

module "lambda_function_from_container_image" {
  source = "terraform-aws-modules/lambda/aws"
  version = "3.3.1"

  function_name = "${random_pet.this.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false

  ##################
  # Container Image
  ##################
  image_uri    = module.docker_image.image_uri
  package_type = "Image"
  architectures = [ "x86_64" ]
}

module "lambda_s3_trigger" {
  source = "terraform-aws-modules/s3-bucket/aws//modules/notification"
  version = "3.3.0"

  bucket = "bucket-oh-bucket-${var.environment}"
  eventbridge = true

  lambda_notifications = {
    lambda1 = {
      function_arn = module.lambda_function_from_container_image.lambda_function_arn
      function_name = module.lambda_function_from_container_image.lambda_function_name
      events = ["s3:ObjectCreated:Put"]
    }
  }
}

module "docker_image" {
  source = "terraform-aws-modules/lambda/aws//modules/docker-build"
  version = "3.3.1"

  create_ecr_repo = true
  ecr_repo        = random_pet.this.id
  ecr_repo_lifecycle_policy = jsonencode({
    "rules" : [
      {
        "rulePriority" : 1,
        "description" : "Keep only the last 2 images",
        "selection" : {
          "tagStatus" : "any",
          "countType" : "imageCountMoreThan",
          "countNumber" : 2
        },
        "action" : {
          "type" : "expire"
        }
      }
    ]
  })

  # docker tag
  image_tag   = var.image_tag

  # the path where the dockerfile and lambda is located
  source_path = "${path.cwd}/context"
  
  # build args
  build_args = {
    FOO = "bar"
  }
}

resource "random_pet" "this" {
  length = 2
}