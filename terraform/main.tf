terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# S3 bucket to store AI Sentinel logs
resource "aws_s3_bucket" "sentinel_logs" {
  bucket = "ai-sentinel-logs-255330795873"

  tags = {
    Name        = "AI Sentinel Logs"
    Environment = "production"
    Project     = "ai-sentinel"
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "sentinel_logs" {
  bucket = aws_s3_bucket.sentinel_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

# CloudWatch Log Group for AI Sentinel
resource "aws_cloudwatch_log_group" "sentinel" {
  name              = "/ai-sentinel/production"
  retention_in_days = 30

  tags = {
    Project     = "ai-sentinel"
    Environment = "production"
  }
}

# CloudWatch Alarm — high spend alert
resource "aws_cloudwatch_metric_alarm" "high_spend" {
  alarm_name          = "ai-sentinel-high-spend"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "TotalSpend"
  namespace           = "AISentinel"
  period              = 300
  statistic           = "Sum"
  threshold           = 4.0
  alarm_description   = "AI spend exceeded $4 — approaching budget limit"

  dimensions = {
    Environment = "production"
  }

  tags = {
    Project = "ai-sentinel"
  }
}

# CloudWatch Alarm — kill switch activated
resource "aws_cloudwatch_metric_alarm" "kill_switch" {
  alarm_name          = "ai-sentinel-kill-switch"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "KillSwitchActivated"
  namespace           = "AISentinel"
  period              = 60
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "AI Sentinel kill switch has been activated!"

  dimensions = {
    Environment = "production"
  }

  tags = {
    Project = "ai-sentinel"
  }
}

# Output values
output "s3_bucket_name" {
  value = aws_s3_bucket.sentinel_logs.bucket
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.sentinel.name
}