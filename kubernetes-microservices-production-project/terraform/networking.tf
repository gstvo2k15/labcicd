resource "azurerm_virtual_network" "vnet" { name="food-vnet" location=var.location resource_group_name=azurerm_resource_group.rg.name address_space=["10.20.0.0/16"] }
resource "azurerm_subnet" "aks" { name="aks-subnet" resource_group_name=azurerm_resource_group.rg.name virtual_network_name=azurerm_virtual_network.vnet.name address_prefixes=["10.20.0.0/20"] }
resource "azurerm_log_analytics_workspace" "logs" { name="food-logs" location=var.location resource_group_name=azurerm_resource_group.rg.name sku="PerGB2018" retention_in_days=30 }
