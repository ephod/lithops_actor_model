# https://docs.digitalocean.com/reference/api/create-personal-access-token/
variable "digital_ocean_token" {
  type        = string
  description = "DigitalOcean personal access token"
  sensitive   = true
}
