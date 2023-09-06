variable "access_key" {
  description = "Access key to AWS console"
}

variable "secret_key" {
  description = "Secret key to AWS console"
}

variable "region" {
  description = "AWS instantiation region"
}

variable "availability_zone" {
  description = "AWS availability zone"
}

variable "initial_database" {
  description = "Name of base psql database"
}

variable "database_name" {
  description = "Name of RDS database"
}

variable "database_username" {
  description = "Username of RDS database"
}

variable "database_password" {
  description = "Password of RDS database"
}

variable "database_ip" {
  description = "IP/HOST URL of the RDS database"
}

variable "database_port" {
  description = "Port used to access RDS database"
}

variable "email" {
  description = "Email address to send alerts to"
}

variable "bucket_name" {
  description = "Name of s3 bucket to pull info from"
}
