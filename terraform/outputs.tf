output "namespace_name" {
  description = "Name of the Terraform-managed namespace"
  value       = module.namespace.namespace_name
}

output "config_map_name" {
  description = "Name of the application ConfigMap"
  value       = module.namespace.config_map_name
}

output "service_account_name" {
  description = "Name of the application ServiceAccount"
  value       = module.namespace.service_account_name
}

output "resource_quota_name" {
  description = "Name of the namespace ResourceQuota"
  value       = module.namespace.resource_quota_name
}
