resource "azurerm_resource_group" "this" {name=var.resource_group_name, location=var.location}
module "networking" {source="./modules/networking", resource_group_name=azurerm_resource_group.this.name, location=var.location}
module "acr" {source="./modules/acr", resource_group_name=azurerm_resource_group.this.name, location=var.location, name=var.acr_name}
module "aks" {source="./modules/aks", resource_group_name=azurerm_resource_group.this.name, location=var.location, name=var.aks_name, subnet_id=module.networking.subnet_id}
module "monitoring" {source="./modules/monitoring", resource_group_name=azurerm_resource_group.this.name, location=var.location}
