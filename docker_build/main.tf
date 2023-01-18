terraform {
  required_version = ">= 1.1.1"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "2.25.0"
    }
  }
}

provider "docker" {}

resource "docker_registry_image" "helloworld" {
  name = "helloworld:1.0"

  build {
    context = "${path.cwd}/context"
  }
}
