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

resource "kubernetes_config_map_v1" "app_config" {
  metadata {
    name      = "capstone-app-config"
    namespace = kubernetes_namespace_v1.capstone.metadata[0].name
  }

  data = {
    APP_ENV   = "development"
    APP_NAME  = "devops-capstone"
    LOG_LEVEL = "INFO"
  }
}

resource "kubernetes_service_account_v1" "app_service_account" {
  metadata {
    name      = "capstone-app-sa"
    namespace = kubernetes_namespace_v1.capstone.metadata[0].name
  }
}

resource "kubernetes_resource_quota_v1" "app_quota" {
  metadata {
    name      = "capstone-resource-quota"
    namespace = kubernetes_namespace_v1.capstone.metadata[0].name
  }

  spec {
    hard = {
      pods              = "10"
      "requests.cpu"    = "2"
      "requests.memory" = "2Gi"
      "limits.cpu"      = "4"
      "limits.memory"   = "4Gi"
    }
  }
}

output "namespace_name" {
  value = kubernetes_namespace_v1.capstone.metadata[0].name
}

output "config_map_name" {
  value = kubernetes_config_map_v1.app_config.metadata[0].name
}

output "service_account_name" {
  value = kubernetes_service_account_v1.app_service_account.metadata[0].name
}

output "resource_quota_name" {
  value = kubernetes_resource_quota_v1.app_quota.metadata[0].name
}
