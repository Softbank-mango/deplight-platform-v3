# DynamoDB Table for Garden State
resource "aws_dynamodb_table" "garden_state" {
  name           = "${var.app_name}-garden-state"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "deployment_id"
  range_key      = "timestamp"

  attribute {
    name = "deployment_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "branch"
    type = "S"
  }

  attribute {
    name = "state"
    type = "S"
  }

  # Global Secondary Index for querying by branch
  global_secondary_index {
    name            = "BranchIndex"
    hash_key        = "branch"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # Global Secondary Index for querying by state
  global_secondary_index {
    name            = "StateIndex"
    hash_key        = "state"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Enable encryption at rest
  server_side_encryption {
    enabled = true
  }

  # TTL to automatically clean up old entries
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${var.app_name}-garden-state"
  }
}

# DynamoDB Table for AI Analysis Results
resource "aws_dynamodb_table" "ai_analysis" {
  name           = "${var.app_name}-ai-analysis"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "analysis_id"
  range_key      = "timestamp"

  attribute {
    name = "analysis_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  attribute {
    name = "repository"
    type = "S"
  }

  attribute {
    name = "commit_sha"
    type = "S"
  }

  # Global Secondary Index for querying by repository
  global_secondary_index {
    name            = "RepositoryIndex"
    hash_key        = "repository"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # Global Secondary Index for querying by commit SHA
  global_secondary_index {
    name            = "CommitIndex"
    hash_key        = "commit_sha"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${var.app_name}-ai-analysis"
  }
}

# DynamoDB Table for Deployment History (for Garden Exhibition)
resource "aws_dynamodb_table" "deployment_history" {
  name           = "${var.app_name}-deployment-history"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "success"
    type = "N"
  }

  attribute {
    name = "deployed_at"
    type = "S"
  }

  # Global Secondary Index for querying successful deployments
  global_secondary_index {
    name            = "SuccessfulDeploymentsIndex"
    hash_key        = "success"
    range_key       = "deployed_at"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  # No TTL - we want to keep successful deployments as "flowers in garden"

  tags = {
    Name = "${var.app_name}-deployment-history"
  }
}
