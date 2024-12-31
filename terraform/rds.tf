resource "aws_db_instance" "example" {
  identifier        = "example-mysql-db-instance"  # RDS 인스턴스 이름
  engine            = "mysql"                       # MySQL 엔진
  engine_version    = "8.0"                         # MySQL 버전 (예: 8.0)
  instance_class    = "db.m6g.large"                 # 인스턴스 타입
  allocated_storage = 100                           # 스토리지 크기 (GB)
  storage_type      = "gp3"                         # 스토리지 타입 (일반 SSD)
  username          = "admin"                       # DB 사용자명
  password          = "your_password"              # DB 비밀번호
  db_name           = "moviedb"                  # 데이터베이스 이름
  port              = 3306                         # MySQL 기본 포트
  publicly_accessible = true                       # 퍼블릭 액세스 허용 (필요에 따라 설정)
  vpc_security_group_ids = [aws_security_group.sg.id]  # 보안 그룹
  multi_az           = false                       # Multi-AZ 배포 (필요에 따라 설정)

  db_subnet_group_name = aws_db_subnet_group.example.name

  tags = {
    Name = "example-mysql-db-instance"
  }
}

# 보안 그룹 설정 (RDS 인스턴스 접근을 허용할 보안 그룹 설정)
resource "aws_security_group" "sg" {
  name        = "example-mysql-rds-sg"
  description = "Allow access to MySQL RDS instance"

  vpc_id = module.vpc.vpc_id
  
  ingress {
    from_port   = 3306  # MySQL 포트
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "example" {
  name        = "example-db-subnet-group"
  subnet_ids  = module.vpc.public_subnets
  description = "My RDS DB subnet group"
}