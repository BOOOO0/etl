
# resource "aws_redshift_subnet_group" "example" {
#   name       = "redshift-subnet-group"
#   subnet_ids = module.vpc.public_subnets

#   tags = {
#     Environment = "data-engineering"
#   }
# }

# resource "aws_security_group" "redshift_sg" {
#   name        = "redshift-security-group"
#   description = "Security group for Redshift cluster"
#   vpc_id      = module.vpc.vpc_id

#   # 인바운드 규칙: VPC 내부 서브넷 CIDR 범위만 허용
#   ingress {
#     description = "Allow Redshift access from VPC internal subnets"
#     from_port   = 5439
#     to_port     = 5439
#     protocol    = "tcp"
#     cidr_blocks = module.vpc.public_subnets_cidr_blocks
#   }

#   # 아웃바운드 규칙 (모든 아웃바운드 허용)
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     Name = "Redshift Security Group"
#   }
# }

# resource "aws_redshift_cluster" "example" {
#   cluster_identifier = "data-engineering-redshift"
#   node_type          = "ra3.xlplus" # RA3 node type
#   number_of_nodes    = 2
#   database_name      = "analytics"
#   master_username    = "admin"
#   master_password    = "Password1234"

#   cluster_subnet_group_name = aws_redshift_subnet_group.example.name
  
#   vpc_security_group_ids = [aws_security_group.redshift_sg.id]

#   tags = {
#     Environment = "data-engineering"
#   }
# }
