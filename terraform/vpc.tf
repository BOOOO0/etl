module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"

  name = "data-engineering-vpc"
  cidr = "10.0.0.0/16"

  azs            = ["ap-northeast-2a", "ap-northeast-2b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]

  enable_nat_gateway = false

  tags = {
    Environment = "data-engineering"
  }
}