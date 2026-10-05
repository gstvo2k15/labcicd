resource "azurerm_virtual_network" "this" {
  name = "${var.project}-vnet"
  location = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  address_space = ["10.20.0.0/16"]
}
resource "azurerm_subnet" "aks" {
  name = "aks-subnet"
  resource_group_name = azurerm_resource_group.this.name
  virtual_network_name = azurerm_virtual_network.this.name
  address_prefixes = ["10.20.1.0/24"]
}
