# ==============================================================================
# Amazon S3 Frontend Static Website Hosting
# AWS Resource: Amazon S3 Bucket configured for static website hosting.
# ==============================================================================

# S3 Bucket: Stores the compiled React/Vite single-page application static build assets.
resource "aws_s3_bucket" "frontend" {
  bucket        = "${var.project_name}-frontend-${var.environment}-${random_id.bucket_suffix.hex}"
  force_destroy = true # Simplifies teardown during grading/viva without leaving orphaned files

  tags = {
    Name = "${var.project_name}-frontend"
  }
}

# S3 Website Configuration: Configures bucket to serve index.html for root and SPA client-side route fallback.
resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

# S3 Public Access Block: Explicitly permits public read access required for static website web hosting.
resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 Bucket Policy: Grants public read permissions (s3:GetObject) to web browsers fetching website assets.
resource "aws_s3_bucket_policy" "frontend_public_read" {
  bucket = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.frontend]
}
