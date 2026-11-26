variable "kubeconfig_path" {
  description = "Path to the Kubernetes configuration file"
  type        = string
  default     = "~/.kube/config"
}

variable "namespace_name" {
  description = "Name of the Kubernetes namespace"
  type        = string
  default     = "capstone-infra"
}
