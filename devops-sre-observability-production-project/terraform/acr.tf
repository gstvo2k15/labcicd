resource "azurerm_container_registry" "this" {
  name = replace("${var.project}acr", "-", "")
  resource_group_name = azurerm_resource_group.this.name
  location = azurerm_resource_group.this.location
  sku = "Standard"
  admin_enabled = false
}
