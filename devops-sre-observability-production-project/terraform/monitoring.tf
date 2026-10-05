resource "azurerm_monitor_diagnostic_setting" "aks" {
  name = "aks-diagnostics"
  target_resource_id = azurerm_kubernetes_cluster.this.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id
  enabled_log { category = "kube-apiserver" }
  enabled_log { category = "kube-audit" }
  enabled_metric { category = "AllMetrics" }
}
