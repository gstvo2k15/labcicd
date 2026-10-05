variable "location" { type=string; default="Central India" }
variable "resource_group_name" { type=string; default="rg-food-delivery-prod" }
variable "aks_name" { type=string; default="aks-food-delivery" }
variable "acr_name" { type=string; default="fooddeliveryacr12345" }
variable "node_count" { type=number; default=2 }
variable "node_vm_size" { type=string; default="Standard_D4s_v5" }
