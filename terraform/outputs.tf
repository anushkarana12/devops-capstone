output "namespace_name" {
  description = "Name of the Terraform-managed Kubernetes namespace"
  value       = module.namespace.namespace_name
}
