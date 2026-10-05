# Terraform hands-on

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Review the plan. Do not put credentials in `.tf` files or `terraform.tfvars`.
