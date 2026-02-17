#!/bin/bash

# Find the S3 bucket associated with CloudFront distribution
echo "🔍 Finding S3 bucket for CloudFront distribution E3CAAI97MXY83V..."

aws cloudfront get-distribution --id E3CAAI97MXY83V \
  --query 'Distribution.DistributionConfig.Origins.Items[0].DomainName' \
  --output text
