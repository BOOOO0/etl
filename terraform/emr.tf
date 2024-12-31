resource "aws_security_group" "emr_master" {
  name_prefix = "emr-master-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.ip] # Apache Airflow
  }

  ingress {
    from_port   = 18080
    to_port     = 18080
    protocol    = "tcp"
    cidr_blocks = [var.ip] # Spark History UI
  }

    ingress {
    from_port   = 8088
    to_port     = 8088
    protocol    = "tcp"
    cidr_blocks = [var.ip] # YARN Manager UI
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ip] # SSH access
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "emr-master-sg"
  }
}

resource "aws_security_group" "emr_slave" {
  name_prefix = "emr-slave-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 8088
    to_port     = 8088
    protocol    = "tcp"
    cidr_blocks = module.vpc.public_subnets_cidr_blocks # YARN Resource Manager
  }

  ingress {
    from_port   = 8042
    to_port     = 8042
    protocol    = "tcp"
    cidr_blocks = module.vpc.public_subnets_cidr_blocks # Node Manager
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "emr-slave-sg"
  }
}


resource "aws_emr_cluster" "example" {
  name          = "data-engineering-emr"
  release_label = "emr-6.13.0"
  applications  = ["Hadoop", "Spark"]
 
  log_uri      = "s3://${aws_s3_bucket.project_bucket.bucket}/emr-logs/"
  
  ec2_attributes {
    instance_profile              = aws_iam_instance_profile.emr_ec2_instance_profile.arn
    # service_access_security_group = aws_security_group.emr_service_access.id
    additional_master_security_groups = aws_security_group.emr_master.id
    
    key_name= "EC2_Key"
    subnet_id                          = module.vpc.public_subnets[0]
    emr_managed_master_security_group = aws_security_group.emr_master.id
    emr_managed_slave_security_group  = aws_security_group.emr_slave.id
  }

  service_role = aws_iam_role.emr_service_role.arn
  autoscaling_role = aws_iam_role.emr_autoscaling_role.arn

  master_instance_group {
    instance_type = "m5.xlarge"
    instance_count = 1
  }
  ebs_root_volume_size = 50 # EBS root volume size in GB for master and core nodes



  core_instance_group {
    instance_type = "m5.xlarge"
    instance_count = 2

    # EBS volumes for core nodes
    ebs_config {
      size                 = 100 # EBS volume size in GB
      type                 = "gp3"
      volumes_per_instance = 1
    }
  }

#   configurations_json = file("emr-config.json")

  # step {
  #   name       = "Spark ETL Job"
  #   action_on_failure = "CONTINUE"
  #   hadoop_jar_step {
  #     jar   = "command-runner.jar"
  #     args  = ["spark-submit", "--deploy-mode", "cluster", "s3://your-code-bucket/scripts/etl_job.py"]
  #   }
  # }

  tags = {
    Environment = "data-engineering"
  }
}

resource "aws_iam_role" "emr_service_role" {
  name = "EMR_DefaultRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "elasticmapreduce.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emr_service_role_policy" {
  role       = aws_iam_role.emr_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceRole"
}

resource "aws_iam_role" "emr_ec2_instance_role" {
  name = "EMR_EC2_DefaultRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emr_ec2_instance_role_policy" {
  role       = aws_iam_role.emr_ec2_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role"
}

resource "aws_iam_instance_profile" "emr_ec2_instance_profile" {
  name = "EMR_EC2_DefaultRole"
  role = aws_iam_role.emr_ec2_instance_role.name
}

resource "aws_iam_role" "emr_autoscaling_role" {
  name = "EMR_AutoScaling_DefaultRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "elasticmapreduce.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emr_autoscaling_role_policy" {
  role       = aws_iam_role.emr_autoscaling_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforAutoScalingRole"
}

resource "aws_iam_policy" "emr_custom_policy" {
  name = "EMR_CustomPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:DescribeSecurityGroups",
          "ec2:CreateSecurityGroup",
          "ec2:DeleteSecurityGroup",
          "ec2:DescribeInstances",
          "ec2:RunInstances",
          "ec2:TerminateInstances",
          "ec2:DescribeSubnets",
          "ec2:DescribeRouteTables",
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emr_ec2_custom_policy_attachment" {
  role       = aws_iam_role.emr_ec2_instance_role.name
  policy_arn = aws_iam_policy.emr_custom_policy.arn
}

resource "aws_iam_role_policy_attachment" "emr_s3_access_policy" {
  role       = aws_iam_role.emr_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess" # S3에 전체 접근 허용
}

resource "aws_iam_policy" "emr_redshift_policy" {
  name = "EMR_RedshiftPolicy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "redshift:GetClusterCredentials",
          "redshift:DescribeClusters",
          "redshift:BatchExecuteStatement",
          "redshift:DescribeTable",
          "redshift:GetQueryResults",
          "redshift:ExecuteQuery",
          "redshift:ListSchemas",
          "redshift:ListTables"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "emr_redshift_policy_attachment" {
  role       = aws_iam_role.emr_service_role.name
  policy_arn = aws_iam_policy.emr_redshift_policy.arn
}