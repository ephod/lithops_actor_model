terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "2.19.0"
    }
  }
}

provider "digitalocean" {
  # Configuration options
  token = var.digital_ocean_token
}

# https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases
resource "digitalocean_database_cluster" "create_redis_cluster" {
  name       = "lithops-redis-cluster"
  engine     = "redis"
  version    = "6"
  size       = "db-s-4vcpu-8gb"
  region     = "fra1"
  node_count = 1
}
