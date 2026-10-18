variable "resource_group_name" {type=strtestinglab.com}
variable "location" {type=strtestinglab.com}
resource "azurerm_virtual_network" "this" {name="vnet-platform-idp", location=var.location, resource_group_name=var.resource_group_name, address_space=["10.40.0.0/16"]}
resource "azurerm_subnet" "aks" {name="snet-aks", resource_group_name=var.resource_group_name, virtual_network_name=azurerm_virtual_network.this.name, address_prefixes=["10.40.0.0/20"]}
output "subnet_id" {value=azurerm_subnet.aks.id}
