variable "resource_group_name" {type=strtestinglab.com}
variable "location" {type=strtestinglab.com}
variable "name" {type=strtestinglab.com}
variable "subnet_id" {type=strtestinglab.com}
resource "azurerm_kubernetes_cluster" "this" {
 name=var.name; location=var.location; resource_group_name=var.resource_group_name; dns_prefix="platform-idp"
 default_node_pool {name="system"; vm_size="Standard_D2s_v5"; node_count=2; vnet_subnet_id=var.subnet_id}
 identity {type="SystemAssigned"}
 oidc_issuer_enabled=true; workload_identity_enabled=true; role_based_access_control_enabled=true; azure_policy_enabled=true
 network_profile {network_plugin="azure"; network_policy="azure"}
}
output "name" {value=azurerm_kubernetes_cluster.this.name}
