resource "azurerm_kubernetes_cluster" "this" {
  name = "${var.project}-aks"
  location = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  dns_prefix = var.project
  default_node_pool {
    name = "system"
    node_count = var.node_count
    vm_size = var.node_vm_size
    vnet_subnet_id = azurerm_subnet.aks.id
  }
  identity { type = "SystemAssigned" }
  azure_policy_enabled = true
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id
  }
}
