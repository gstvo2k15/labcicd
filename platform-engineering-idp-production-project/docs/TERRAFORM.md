# Terraform

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
cd terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Destroy the lab when finished:

```bash
terraform destroy
```
