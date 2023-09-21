provider "aws" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
}

#Cohort 8 VPC

data "aws_vpc" "cohort-8-VPC" {
  id = "vpc-0e0f897ec7ddc230d"
}

# Cohort 8 Subnet

data "aws_subnet" "cohort-8-public-subnet-1" {
  vpc_id            = data.aws_vpc.cohort-8-VPC.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-west-2a"
}

data "aws_subnet" "cohort-8-public-subnet-2" {
  vpc_id            = data.aws_vpc.cohort-8-VPC.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-west-2b"
}

data "aws_subnet" "cohort-8-public-subnet-3" {
  vpc_id            = data.aws_vpc.cohort-8-VPC.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "eu-west-2c"
}

output "cohort-8-public-subnet-ids" {
  value = [
    data.aws_subnet.cohort-8-public-subnet-1.id,
    data.aws_subnet.cohort-8-public-subnet-2.id,
    data.aws_subnet.cohort-8-public-subnet-3.id,
  ]
}

# RSS ECR

resource "aws_ecr_repository" "media-sentiment-rss-ecr" {
  name         = "media-sentiment-rss-ecr"
  force_delete = true
}

# RSS Lambda

resource "aws_iam_role" "media-sentiment-rss-lambda-role" {
  name = "media-sentiment-rss-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_lambda_function" "media-sentiment-rss-lambda" {
  function_name = "media-sentiment-rss-lambda"
  role          = resource.aws_iam_role.media-sentiment-rss-lambda-role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/media-sentiment-rss-ecr:latest"
  architectures = ["x86_64"]
  package_type  = "Image"
  memory_size = 256
  ephemeral_storage {
    size = 512
  }
  timeout = 600
  environment {
    variables = {
      INITIAL_DATABASE  = var.initial_database
      DATABASE_NAME     = var.database_name
      DATABASE_PASSWORD = var.database_password
      DATABASE_PORT     = var.database_port
      DATABASE_USERNAME = var.database_username
      DATABASE_IP       = aws_db_instance.media-sentiment-rds.address
      ACCESS_KEY_ID     = var.access_key
      SECRET_ACCESS_KEY = var.secret_key
    }
  }
}

# RSS Scheduler

resource "aws_iam_role" "media-sentiment-rss-scheduler-role" {
  name = "media-sentiment-rss-scheduler-role"
  assume_role_policy = jsonencode({
  Version = "2012-10-17",
  Statement = [
    {
      Effect = "Allow",
      Principal = {
        Service = "scheduler.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }
  ]
})
  inline_policy {
    name = "media-sentiment-rss-inline-policy"

    policy = jsonencode({
	Version= "2012-10-17",
	Statement = [
		{
			Effect= "Allow",
			Action= "lambda:InvokeFunction"
      Resource= [
                "arn:aws:lambda:eu-west-2:129033205317:function:media-sentiment-rss-lambda:*",
                "arn:aws:lambda:eu-west-2:129033205317:function:media-sentiment-rss-lambda"
            ]
		},
    ]
})
}
}

resource "aws_scheduler_schedule" "media-sentiment-rss-pipeline-scheduler" {
  name                         = "media-sentiment-rss-pipeline-scheduler"
  schedule_expression_timezone = "Europe/London"
  description                  = "Schedule to run ETL pipeline every hour"
  state                        = "ENABLED"
  
  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 * * * ? *)"

  target {
    arn      = aws_lambda_function.media-sentiment-rss-lambda.arn
    role_arn = aws_iam_role.media-sentiment-rss-scheduler-role.arn
  }
}

# Media Sentiment RDS

resource "aws_security_group" "media-sentiment-rds-sg" {
  vpc_id = data.aws_vpc.cohort-8-VPC.id
  name = "media-sentiment-rds-sg"
  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    cidr_blocks = ["86.155.163.236/32"]
  }
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "media-sentiment-rds" {
  identifier="media-sentiment-rds"
  allocated_storage    = 20
  db_name              = var.database_name
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  username             = var.database_username
  password             = var.database_password
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  performance_insights_enabled = false
  db_subnet_group_name = "public_subnet_group"
  publicly_accessible = true
  vpc_security_group_ids = ["${resource.aws_security_group.media-sentiment-rds-sg.id}"]
}

# ECS IAM Role

resource "aws_iam_role" "ecs-task-execution-role" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Effect = "Allow",
        Sid    = ""
      }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs-task-execution-role-policy-attachment" {
  role       = aws_iam_role.ecs-task-execution-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Cluster

resource "aws_ecs_cluster" "media-sentiment-cluster" {
  name = "media-sentiment-cluster"
}

# Public Sentiment ECR

resource "aws_ecr_repository" "media-sentiment-public-sentiment-ecr" {
  name         = "media-sentiment-public-sentiment-ecr"
  force_delete = true
}

# Public Sentiment ECS

resource "aws_security_group" "media-sentiment-ecs-sg" {
  name = "media-sentiment-ecs-sg"
  vpc_id = data.aws_vpc.cohort-8-VPC.id
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

resource "aws_ecs_task_definition" "media-sentiment-public-sentiment-ecs" {
  family                   = "media-sentiment-public-sentiment-ecs"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs-task-execution-role.arn

  container_definitions = jsonencode([
    {
      "name" : "media-sentiment-public-sentiment-pipeline",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/media-sentiment-public-sentiment-ecr:latest",
      "portMappings" : [
        {
          "name" : "80-mapping",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "DATABASE_NAME",
          "value" : var.database_name
        },
        {
          "name" : "DATABASE_USERNAME",
          "value" : var.database_username
        },
        {
          "name" : "DATABASE_IP",
          "value" : aws_db_instance.media-sentiment-rds.address
        },
        {
          "name" : "ACCESS_KEY",
          "value" : var.access_key
        },
        {
          "name" : "SECRET_KEY",
          "value" : var.secret_key
        },
        {
          "name" : "BUCKET_NAME",
          "values" : var.bucket_name
        },
        {
          "name" : "DATABASE_PASSWORD",
          "value" : var.database_password
        },
        {
          "name" : "REDDIT_TOPIC",
          "value" : var.reddit_topic
        },
        {
          "name" : "REDDIT_JSON_BUCKET_NAME",
          "value" : var.reddit_json_bucket_name
        },
        {
          "name" : "REDDIT_CLIENT_SECRET",
          "value" : var.reddit_client_secret
        },
        {
          "name" : "REDDIT_SECRET_KEY",
          "value" : var.reddit_secret_key
        },
        {
          "name" : "REDDIT_USERNAME",
          "value" : var.reddit_username
        },
        {
          "name" : "REDDIT_PASSWORD",
          "value" : var.reddit_password
        }
      ]
    }
  ])
}

# Article Sentiment Pipeline ECR

resource "aws_ecr_repository" "media-sentiment-article-sentiment-ecr" {
  name         = "media-sentiment-article-sentiment-ecr"
  force_delete = true
}

# Article Sentiment Pipeline ECS

resource "aws_ecs_task_definition" "media-sentiment-article-sentiment-ecs" {
  family                   = "media-sentiment-article-sentiment-ecs"
  cpu                      = "1024"
  network_mode             = "awsvpc"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs-task-execution-role.arn

  container_definitions = jsonencode([
    {
      "name" : "media-sentiment-public-sentiment-pipeline",
      "image" : "129033205317.dkr.ecr.eu-west-2.amazonaws.com/media-sentiment-article-sentiment-ecr:latest",
      "portMappings" : [
        {
          "name" : "80-mapping",
          "containerPort" : 80,
          "hostPort" : 80,
          "protocol" : "tcp",
          "appProtocol" : "http"
        }
      ],
      "essential" : true,
      "environment" : [
        {
          "name" : "DATABASE_NAME",
          "value" : var.database_name
        },
        {
          "name" : "DATABASE_USERNAME",
          "value" : var.database_username
        },
        {
          "name" : "DATABASE_ENDPOINT",
          "value" : aws_db_instance.media-sentiment-rds.address
        },
        {
          "name" : "ACCESS_KEY_ID",
          "value" : var.access_key
        },
        {
          "name" : "SECRET_ACCESS_KEY",
          "value" : var.secret_key
        },
        {
          "name" : "BUCKET_NAME",
          "value" : var.bucket_name
        },
        {
          "name" : "DATABASE_PASSWORD",
          "value" : var.database_password
        },
        {
          "name" : "OPENAI_API_KEY",
          "value" : var.openai_api_key
        }
      ]
    }
  ])
}

# Email ECR

resource "aws_ecr_repository" "media-sentiment-email-ecr" {
  name         = "media-sentiment-email-ecr"
  force_delete = true
}

# Email Lambda

resource "aws_iam_role" "media-sentiment-email-lambda-role" {
  name = "media-sentiment-email-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda-read-bucket-policy" {
  role       = aws_iam_role.media-sentiment-email-lambda-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_lambda_function" "media-sentiment-email-lambda" {
  function_name = "media-sentiment-email-lambda"
  role          = resource.aws_iam_role.media-sentiment-email-lambda-role.arn
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/media-sentiment-email-ecr:latest"
  architectures = ["x86_64"]
  package_type  = "Image"
  memory_size = 2048
  ephemeral_storage {
    size = 512
  }
  timeout = 600
  environment {
    variables = {
      INITIAL_DATABASE  = var.initial_database
      DATABASE_NAME     = var.database_name
      DATABASE_PASSWORD = var.database_password
      DATABASE_PORT     = var.database_port
      DATABASE_USERNAME = var.database_username
      DATABASE_IP       = aws_db_instance.media-sentiment-rds.address
      ACCESS_KEY     = var.access_key
      SECRET_KEY = var.secret_key
      BUCKET_NAME       = var.email_bucket_name
      EMAIL_SENDER = var.email_sender
      EMAIL_RECIPIENT = var.email_recipient
    }
  }
}

# S3 reddit bucket

resource "aws_s3_bucket" "media-sentiment-reddit-json-short-term" {
  bucket = "media-sentiment-reddit-json-short-term"
}

resource "aws_s3_bucket_lifecycle_configuration" "media-sentiment-reddit-json-long-term" {
  rule {
    id      = "media-sentiment-reddit-json-long-term-rule"
    status  = "Enabled"

    transition {
      days          = 1
      storage_class = "GLACIER_IR"
    }
  }

  bucket = aws_s3_bucket.media-sentiment-reddit-json-short-term.id
}

# S3 report pdf bucket

resource "aws_s3_bucket" "media-sentiment-pdf-reports-short-term" {
  bucket = "media-sentiment-pdf-reports-short-term"
}

resource "aws_s3_bucket_lifecycle_configuration" "media-sentiment-pdf-reports-long-term" {
  rule {
    id      = "media-sentiment-pdf-reports-long-term-rule"
    status  = "Enabled"

    transition {
      days          = 1
      storage_class = "GLACIER_IR"
    }
  }

  bucket = aws_s3_bucket.media-sentiment-pdf-reports-short-term.id
}

# State Machine

resource "aws_iam_role" "media-sentiment-state-machine-role" {
  name = "media-sentiment-state-machine-role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Principal": {
          "Service": "states.amazonaws.com"
        },
        "Effect": "Allow",
        "Sid": ""
      }
    ]
  })
  inline_policy {
    name = "media-sentiment-sf-ecs-inline-policy"

    policy = jsonencode({
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": "ecs:RunTask",
			"Resource": "*"
		}
	]
})
}
  inline_policy {
    name = "media-sentiment-sf-lambda-inline-policy"

    policy = jsonencode({
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": "lambda:InvokeFunction",
			"Resource": "*"
		}
	]
})
}
  inline_policy {
    name = "media-sentiment-sf-iam-inline-policy"

    policy = jsonencode ({
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": "iam:PassRole",
			"Resource": "*"
		}
	]
})
}
  inline_policy {
    name = "media-sentiment-sf-sync-inline-policy"

    policy = jsonencode ({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "states:StartExecution"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "states:DescribeExecution",
                "states:StopExecution"
            ],
            "Resource": [
               "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "events:PutTargets",
                "events:PutRule",
                "events:DescribeRule"
            ],
            "Resource": [
               "*"
            ]
        }
    ]
})
}
}

resource "aws_sfn_state_machine" "media-sentiment-state-machine" {
  name     = "media-sentiment-state-machine"
  role_arn = resource.aws_iam_role.media-sentiment-state-machine-role.arn

  definition = <<EOF
{
  "Comment": "State machine that runs the article sentiment ECS, public sentiment ECS, and email lambda",
  "StartAt": "reddit-ecs",
  "States": {
    "reddit-ecs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "arn:aws:ecs:eu-west-2:129033205317:cluster/media-sentiment-cluster",
        "TaskDefinition": "arn:aws:ecs:eu-west-2:129033205317:task-definition/media-sentiment-public-sentiment-ecs",
        "NetworkConfiguration": {
      "AwsvpcConfiguration": {
         "AssignPublicIp": "ENABLED",
         "SecurityGroups": ["sg-0ac19c4c6eb7d1ca3"],
         "Subnets": ["subnet-03b1a3e1075174995", "subnet-0cec5bdb9586ed3c4","subnet-0667517a2a13e2a6b"]
      }
      }
      },
      "Next": "tagging-ecs"
    },
    "tagging-ecs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "LaunchType": "FARGATE",
        "Cluster": "arn:aws:ecs:eu-west-2:129033205317:cluster/media-sentiment-cluster",
        "TaskDefinition": "arn:aws:ecs:eu-west-2:129033205317:task-definition/media-sentiment-article-sentiment-ecs",
        "NetworkConfiguration": {
      "AwsvpcConfiguration": {
         "AssignPublicIp": "ENABLED",
         "SecurityGroups": ["sg-0ac19c4c6eb7d1ca3"],
         "Subnets": ["subnet-03b1a3e1075174995", "subnet-0cec5bdb9586ed3c4","subnet-0667517a2a13e2a6b"]
      }
      }
      },
      "Next": "Email Lambda Invoke"
    },
    "Email Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "OutputPath": "$.Payload",
      "Parameters": {
        "Payload.$": "$",
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:media-sentiment-email-lambda:$LATEST"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 6,
          "BackoffRate": 2
        }
      ],
      "End": true
    }
  }
}
EOF
}

# 6 Hour Scheduler

resource "aws_iam_role" "media-sentiment-six-scheduler-role" {
  name = "media-sentiment-six-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com",
        },
        Action = "sts:AssumeRole",
      },
    ],
  })
  inline_policy {
    name = "media-sentiment-scheduler-inline-policy"

    policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "states:StartExecution",
        Resource = aws_sfn_state_machine.media-sentiment-state-machine.arn,
      },
    ],
  })
}
}

resource "aws_scheduler_schedule" "media-sentiment-state-machine-schedule" {
  name                         = "media-sentiment-state-machine-schedule"
  schedule_expression_timezone = "Europe/London"
  description                  = "Schedule to start Step Function execution every 6 hours"
  state                        = "ENABLED"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 */6 * * ? *)"

  target {
    arn      = "arn:aws:states:eu-west-2:129033205317:stateMachine:media-sentiment-state-machine"
    role_arn = aws_iam_role.media-sentiment-six-scheduler-role.arn
    }
}
