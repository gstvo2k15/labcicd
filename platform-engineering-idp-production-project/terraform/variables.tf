variable "subscription_id" {type=string, sensitive=true}
variable "location" {type=string, default="eastus"}
variable "resource_group_name" {type=string, default="rg-platform-idp-dev"}
variable "acr_name" {type=string}
variable "aks_name" {type=string, default="aks-platform-idp-dev"}
