output "resource_group" { value=azurerm_resource_group.rg.name }
output "acr_login_server" { value=azurerm_container_registry.acr.login_server }
output "aks_name" { value=azurerm_kubernetes_cluster.aks.name }
output "aks_get_credentials" { value="az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${azurerm_kubernetes_cluster.aks.name}" }
