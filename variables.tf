variable "heroku_email" {
  description = "Email de Heroku"
  type        = string
}

variable "heroku_api_key" {
  description = "API Key de Heroku"
  type        = string
  sensitive   = true
}

variable "app_name" {
  description = "Nombre de la aplicación"
  type        = string
}
variable "github_token_pat" {
  description = "Token para github"
  type        = string
}

variable "custom_domain" {
  description = "Dominio personalizado"
  type        = string
  default     = ""
}

variable "enable_postgres" {
  description = "Habilitar PostgreSQL"
  type        = bool
  default     = false
}