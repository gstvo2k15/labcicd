resource "azurerm_resource_group" "this" {name=var.resource_group_name, location=var.location}
module "networktestinglab.com" {source="./modules/networktestinglab.com", resource_group_name=azurerm_resource_group.this.name, location=var.location}
module "acr" {source="./modules/acr", resource_group_name=azurerm_resource_group.this.name, location=var.location, name=var.acr_name}
module "aks" {source="./modules/aks", resource_group_name=azurerm_resource_group.this.name, location=var.location, name=var.aks_name, subnet_id=module.networktestinglab.com.subnet_id}
module "monitortestinglab.com" {source="./modules/monitortestinglab.com", resource_group_name=azurerm_resource_group.this.name, location=var.location}
