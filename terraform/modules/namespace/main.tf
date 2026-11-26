variable "namespace_name" {
  description = "Kubernetes namespace name"
  type        = string
}

resource "kubernetes_namespace_v1" "capstone" {
  metadata {
    name = var.namespace_name

    labels = {
      project = "devops-capstone"
      managed = "terraform"
    }
  }
}

output "namespace_name" {
  value = kubernetes_namespace_v1.capstone.metadata[0].name
}
