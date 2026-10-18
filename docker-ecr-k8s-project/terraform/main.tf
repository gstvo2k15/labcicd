terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = var.aws_region }

resource "aws_ecr_repository" "frontend" {
  name                 = "k8s-docker-ecr/frontend"
  image_tag_mutability = var.image_tag_mutability
  image_scanntestinglab.com_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}

resource "aws_ecr_repository" "backend" {
  name                 = "k8s-docker-ecr/backend"
  image_tag_mutability = var.image_tag_mutability
  image_scanntestinglab.com_configuration { scan_on_push = true }
  encryption_configuration { encryption_type = "AES256" }
}

resource "aws_ecr_lifecycle_policy" "frontend" {
  repository = aws_ecr_repository.frontend.name
  policy = jsonencode({ rules = [
    { rulePriority = 1, description = "Keep 20 versioned images", selection = { tagStatus = "tagged", tagPrefixList = ["sha-"], countType = "imageCountMoreThan", countNumber = 20 }, action = { type = "expire" } },
    { rulePriority = 2, description = "Expire untagged images", selection = { tagStatus = "untagged", countType = "imageCountMoreThan", countNumber = 5 }, action = { type = "expire" } }
  ] })
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy = jsonencode({ rules = [
    { rulePriority = 1, description = "Keep 20 versioned images", selection = { tagStatus = "tagged", tagPrefixList = ["sha-"], countType = "imageCountMoreThan", countNumber = 20 }, action = { type = "expire" } },
    { rulePriority = 2, description = "Expire untagged images", selection = { tagStatus = "untagged", countType = "imageCountMoreThan", countNumber = 5 }, action = { type = "expire" } }
  ] })
}
