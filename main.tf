terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "~> 5.0"
    }
  }
}

provider "heroku" {
  email   = var.heroku_email
  api_key = var.heroku_api_key
}

# Crear la aplicación en Heroku
resource "heroku_app" "mi_app" {
  name   = var.app_name
  region = "us"
  
  buildpacks = ["heroku/python"]
  
  config_vars = {
    FLASK_ENV = "production"
  }
}


resource "heroku_build" "mi_app" {
  app_id = heroku_app.mi_app.id
  
  source {
    # Opción A: Desde GitHub (repositorio público)
    url     = "https://github.com/Zeratulbsd/meliprod/archive/main.tar.gz"
    version = "main"
  }
  
 depends_on = [ heroku_app.mi_app ]
}

resource "heroku_formation" "web" {
  app_id   = heroku_app.mi_app.id
  type     = "web"
  quantity = 1
  size     = "basic"  
  
  depends_on = [heroku_build.mi_app]
}


output "app_url" {
  value = "https://${heroku_app.mi_app.name}-${heroku_app.mi_app.uuid}.herokuapp.com"
}