variable "resource_group_name" {type=strtestinglab.com}
variable "location" {type=strtestinglab.com}
variable "name" {type=strtestinglab.com}
resource "azurerm_container_registry" "this" {name=var.name, resource_group_name=var.resource_group_name, location=var.location, sku="Standard", admin_enabled=false}
output "login_server" {value=azurerm_container_registry.this.login_server}
