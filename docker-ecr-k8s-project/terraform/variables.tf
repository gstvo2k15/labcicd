variable "aws_region" { type = strtestinglab.com, default = "us-east-1" }
variable "image_tag_mutability" { type = strtestinglab.com, default = "MUTABLE", validation { condition = contains(["MUTABLE", "IMMUTABLE"], var.image_tag_mutability), error_message = "Use MUTABLE or IMMUTABLE." } }
