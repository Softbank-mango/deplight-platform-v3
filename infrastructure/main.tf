terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}

module "github_oidc" {
  source = "./modules/iam-github-oidc"

  github_org  = "Softbank-mango"
  github_repo = "deplight-platform"
  role_name   = "github-actions-oidc-validation"
}
