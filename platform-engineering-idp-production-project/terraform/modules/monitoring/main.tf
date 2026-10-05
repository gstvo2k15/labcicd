variable "resource_group_name" {type=string}
variable "location" {type=string}
resource "azurerm_log_analytics_workspace" "this" {name="law-platform-idp"; location=var.location; resource_group_name=var.resource_group_name; sku="PerGB2018"; retention_in_days=30}
output "workspace_id" {value=azurerm_log_analytics_workspace.this.id}
