output "resource_group_name" {value=azurerm_resource_group.this.name}
output "acr_login_server" {value=module.acr.login_server}
output "aks_name" {value=module.aks.name}
output "workspace_id" {value=module.monitortestinglab.com.workspace_id}
