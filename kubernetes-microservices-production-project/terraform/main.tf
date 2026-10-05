resource "azurerm_resource_group" "rg" { name=var.resource_group_name; location=var.location }
resource "azurerm_container_registry" "acr" { name=var.acr_name; resource_group_name=azurerm_resource_group.rg.name; location=var.location; sku="Standard"; admin_enabled=false }
resource "azurerm_kubernetes_cluster" "aks" {
 name=var.aks_name; location=var.location; resource_group_name=azurerm_resource_group.rg.name; dns_prefix="food-delivery"
 default_node_pool { name="system"; node_count=var.node_count; vm_size=var.node_vm_size; vnet_subnet_id=azurerm_subnet.aks.id }
 identity { type="SystemAssigned" }
 oidc_issuer_enabled=true; workload_identity_enabled=true
 azure_policy_enabled=true
 oms_agent { log_analytics_workspace_id=azurerm_log_analytics_workspace.logs.id }
 network_profile { network_plugin="azure"; network_policy="azure"; load_balancer_sku="standard" }
}
resource "azurerm_role_assignment" "acr_pull" { scope=azurerm_container_registry.acr.id; role_definition_name="AcrPull"; principal_id=azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id }
