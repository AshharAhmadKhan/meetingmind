#!/usr/bin/env python3
"""
Analyze AWS credit usage and resource utilization for MeetingMind.

This script calculates:
1. Current credit balance
2. Cost per meeting breakdown
3. Estimated meetings remaining
4. Monthly burn rate projections
5. Resource utilization recommendations
"""

import json

# ═══════════════════════════════════════════════════════════════════════════
# CREDIT INFORMATION
# ═══════════════════════════════════════════════════════════════════════════

TOTAL_CREDITS = 340.00  # USD
CREDITS_USED = 0.00  # USD (as of Feb 24, 2026)
CREDITS_REMAINING = 340.00  # USD

# ═══════════════════════════════════════════════════════════════════════════
# COST PER MEETING BREAKDOWN (45-minute meeting with 20K char transcript)
# ═══════════════════════════════════════════════════════════════════════════

# AWS Transcribe (45 min audio)
# Pricing: $0.024 per minute (standard)
TRANSCRIBE_COST_PER_MEETING = 0.024 * 45  # $1.08

# AWS Bedrock - Titan Embeddings (1 embedding per meeting)
# Pricing: $0.0001 per 1K input tokens
# Average: 20K chars = ~5K tokens
TITAN_EMBEDDING_COST = 0.0001 * 5  # $0.0005

# AWS Bedrock - Claude Haiku (primary analysis model)
# Pricing: $0.00025 per 1K input tokens, $0.00125 per 1K output tokens
# Input: 20K chars = ~5K tokens
# Output: ~2K tokens (actions, decisions, summary)
HAIKU_INPUT_COST = 0.00025 * 5  # $0.00125
HAIKU_OUTPUT_COST = 0.00125 * 2  # $0.0025

# AWS DynamoDB (write operations)
# Pricing: $1.25 per million write request units
# Per meeting: ~25 writes (1 meeting + 22 actions + 2 metadata)
DYNAMODB_COST_PER_MEETING = (25 / 1_000_000) * 1.25  # $0.00003125

# AWS SES (email notification)
# Pricing: $0.10 per 1,000 emails
SES_COST_PER_MEETING = 0.10 / 1000  # $0.0001

# AWS Lambda (compute)
# Pricing: $0.20 per 1M requests + $0.0000166667 per GB-second
# Per meeting: ~5 Lambda invocations, ~10 seconds total, 512MB avg
LAMBDA_REQUESTS_COST = (5 / 1_000_000) * 0.20  # $0.000001
LAMBDA_COMPUTE_COST = (10 * 0.5) * 0.0000166667  # $0.00008333

# AWS S3 (audio storage)
# Pricing: $0.023 per GB stored, $0.0004 per 1K GET requests
# Per meeting: ~50MB audio file, 2 GET requests
S3_STORAGE_COST = (0.05 / 1) * 0.023  # $0.00115 per month (amortized)
S3_GET_COST = (2 / 1000) * 0.0004  # $0.0000008

# CloudFront (frontend delivery)
# Pricing: $0.085 per GB data transfer
# Per meeting: ~2MB frontend assets
CLOUDFRONT_COST = (0.002 / 1) * 0.085  # $0.00017

# TOTAL COST PER MEETING
TOTAL_COST_PER_MEETING = (
    TRANSCRIBE_COST_PER_MEETING +
    TITAN_EMBEDDING_COST +
    HAIKU_INPUT_COST +
    HAIKU_OUTPUT_COST +
    DYNAMODB_COST_PER_MEETING +
    SES_COST_PER_MEETING +
    LAMBDA_REQUESTS_COST +
    LAMBDA_COMPUTE_COST +
    S3_STORAGE_COST +
    S3_GET_COST +
    CLOUDFRONT_COST
)

# ═══════════════════════════════════════════════════════════════════════════
# QUOTA LIMITS (AFTER INCREASE)
# ═══════════════════════════════════════════════════════════════════════════

# Bedrock Quotas (per minute)
TITAN_EMBEDDINGS_TPM = 350_000  # tokens per minute
TITAN_EMBEDDINGS_RPM = 7_000  # requests per minute

NOVA_MICRO_TPM = 200_000  # tokens per minute (on-demand)
NOVA_MICRO_RPM = 200  # requests per minute (on-demand)

NOVA_LITE_TPM = 200_000  # tokens per minute (on-demand)
NOVA_LITE_RPM = 200  # requests per minute (on-demand)

HAIKU_TPM = 100_000  # tokens per minute (standard)
HAIKU_RPM = 1_000  # requests per minute (standard)

# Transcribe Quotas
TRANSCRIBE_CONCURRENT_JOBS = 100  # concurrent transcription jobs

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def analyze_cost_breakdown():
    """Print detailed cost breakdown per meeting."""
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                    COST BREAKDOWN PER MEETING (45 min)                   ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  AWS Transcribe (45 min audio):              ${TRANSCRIBE_COST_PER_MEETING:.4f}")
    print(f"  AWS Bedrock - Titan Embeddings:             ${TITAN_EMBEDDING_COST:.4f}")
    print(f"  AWS Bedrock - Claude Haiku (input):         ${HAIKU_INPUT_COST:.4f}")
    print(f"  AWS Bedrock - Claude Haiku (output):        ${HAIKU_OUTPUT_COST:.4f}")
    print(f"  AWS DynamoDB (writes):                      ${DYNAMODB_COST_PER_MEETING:.5f}")
    print(f"  AWS SES (email):                            ${SES_COST_PER_MEETING:.5f}")
    print(f"  AWS Lambda (compute):                       ${LAMBDA_COMPUTE_COST:.5f}")
    print(f"  AWS S3 (storage + GET):                     ${S3_STORAGE_COST + S3_GET_COST:.5f}")
    print(f"  CloudFront (delivery):                      ${CLOUDFRONT_COST:.5f}")
    print("  " + "─" * 75)
    print(f"  TOTAL PER MEETING:                          ${TOTAL_COST_PER_MEETING:.4f}")
    print()
    print(f"  💡 Transcribe is {(TRANSCRIBE_COST_PER_MEETING / TOTAL_COST_PER_MEETING) * 100:.1f}% of total cost")
    print(f"  💡 Bedrock AI is {((HAIKU_INPUT_COST + HAIKU_OUTPUT_COST + TITAN_EMBEDDING_COST) / TOTAL_COST_PER_MEETING) * 100:.1f}% of total cost")
    print()


def analyze_credit_status():
    """Print current credit status and projections."""
    meetings_remaining = int(CREDITS_REMAINING / TOTAL_COST_PER_MEETING)
    
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                         CREDIT STATUS & PROJECTIONS                       ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Total Credits:                              ${TOTAL_CREDITS:.2f}")
    print(f"  Credits Used:                               ${CREDITS_USED:.2f}")
    print(f"  Credits Remaining:                          ${CREDITS_REMAINING:.2f}")
    print()
    print(f"  Cost Per Meeting:                           ${TOTAL_COST_PER_MEETING:.4f}")
    print(f"  Meetings Remaining:                         {meetings_remaining:,} meetings")
    print()
    print("  📊 USAGE SCENARIOS:")
    print(f"     • 10 meetings/day:   {int(meetings_remaining / 10)} days remaining")
    print(f"     • 50 meetings/day:   {int(meetings_remaining / 50)} days remaining")
    print(f"     • 100 meetings/day:  {int(meetings_remaining / 100)} days remaining")
    print()


def analyze_quota_capacity():
    """Print quota capacity and concurrent user support."""
    # Calculate meetings per minute based on bottleneck (Transcribe or Bedrock)
    # Bottleneck: Haiku RPM = 1000 requests/min
    meetings_per_minute = min(HAIKU_RPM, TRANSCRIBE_CONCURRENT_JOBS)
    
    # Calculate concurrent users (assuming 1 meeting per user per session)
    concurrent_users = meetings_per_minute
    
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                      QUOTA CAPACITY & CONCURRENCY                         ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("  BEDROCK QUOTAS (after increase):")
    print(f"     • Titan Embeddings:  {TITAN_EMBEDDINGS_TPM:,} TPM, {TITAN_EMBEDDINGS_RPM:,} RPM")
    print(f"     • Nova Micro:        {NOVA_MICRO_TPM:,} TPM, {NOVA_MICRO_RPM:,} RPM")
    print(f"     • Nova Lite:         {NOVA_LITE_TPM:,} TPM, {NOVA_LITE_RPM:,} RPM")
    print(f"     • Claude Haiku:      {HAIKU_TPM:,} TPM, {HAIKU_RPM:,} RPM")
    print()
    print("  TRANSCRIBE QUOTAS:")
    print(f"     • Concurrent Jobs:   {TRANSCRIBE_CONCURRENT_JOBS} jobs")
    print()
    print("  CAPACITY ANALYSIS:")
    print(f"     • Meetings/minute:   {meetings_per_minute:,} meetings")
    print(f"     • Meetings/hour:     {meetings_per_minute * 60:,} meetings")
    print(f"     • Concurrent users:  {concurrent_users:,} users")
    print()
    print("  ✅ System can handle 100+ concurrent users during competition")
    print()


def analyze_why_credits_unchanged():
    """Explain why credits are still at $340."""
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                    WHY CREDITS ARE STILL AT $340                          ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("  POSSIBLE REASONS:")
    print()
    print("  1. ⏱️  BILLING DELAY")
    print("     AWS credits are typically deducted at the end of the billing cycle")
    print("     (monthly), not in real-time. Your usage is being tracked but not")
    print("     yet reflected in the credit balance.")
    print()
    print("  2. 🆓 FREE TIER COVERAGE")
    print("     Some services have free tier allowances that are used before credits:")
    print("     • Lambda: 1M requests/month free")
    print("     • DynamoDB: 25 GB storage + 25 WCU/RCU free")
    print("     • S3: 5 GB storage + 20K GET requests free")
    print("     • SES: 62K emails/month free (if sending from EC2)")
    print()
    print("  3. 📊 LOW USAGE SO FAR")
    print("     If you've only uploaded a few test meetings, the cost is minimal:")
    print(f"     • 5 meetings = ${TOTAL_COST_PER_MEETING * 5:.2f}")
    print(f"     • 10 meetings = ${TOTAL_COST_PER_MEETING * 10:.2f}")
    print(f"     • 20 meetings = ${TOTAL_COST_PER_MEETING * 20:.2f}")
    print()
    print("  4. 🔍 CREDIT REPORTING LAG")
    print("     AWS Billing Console may take 24-48 hours to update credit usage.")
    print()
    print("  💡 RECOMMENDATION:")
    print("     Check AWS Billing Console → Cost Explorer to see actual usage")
    print("     even if credits haven't been deducted yet.")
    print()


def analyze_optimization_opportunities():
    """Print cost optimization recommendations."""
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                    COST OPTIMIZATION OPPORTUNITIES                        ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print("  CURRENT OPTIMIZATIONS (already implemented):")
    print("     ✅ Using Claude Haiku (cheapest Claude model)")
    print("     ✅ Truncating transcripts to 20K chars (optimal for cost/quality)")
    print("     ✅ Single embedding per meeting (not per action)")
    print("     ✅ Adaptive retry with exponential backoff (reduces wasted calls)")
    print("     ✅ Demo meetings auto-delete after 30 min (saves storage)")
    print()
    print("  POTENTIAL OPTIMIZATIONS (if needed):")
    print()
    print("  1. 💰 SWITCH TO NOVA MODELS (if quality acceptable)")
    print(f"     • Nova Lite input:  $0.00006/1K tokens (vs Haiku $0.00025/1K)")
    print(f"     • Nova Lite output: $0.00024/1K tokens (vs Haiku $0.00125/1K)")
    print(f"     • Savings: ~75% on AI costs = ${(HAIKU_INPUT_COST + HAIKU_OUTPUT_COST) * 0.75:.4f}/meeting")
    print()
    print("  2. 📉 REDUCE TRANSCRIPT LENGTH (if acceptable)")
    print("     • 20K → 15K chars: Save ~$0.0003/meeting")
    print("     • 20K → 10K chars: Save ~$0.0006/meeting")
    print("     • Trade-off: May miss action items in longer meetings")
    print()
    print("  3. 🎯 BATCH PROCESSING (for high volume)")
    print("     • Process multiple meetings in single Lambda invocation")
    print("     • Reduces Lambda cold starts and request costs")
    print("     • Savings: ~$0.00001/meeting")
    print()
    print("  4. 🗜️  COMPRESS AUDIO BEFORE TRANSCRIBE (if quality acceptable)")
    print("     • Convert to lower bitrate MP3 (64 kbps vs 128 kbps)")
    print("     • Reduces S3 storage and transfer costs")
    print("     • Savings: ~$0.0005/meeting")
    print()
    print("  💡 RECOMMENDATION:")
    print("     Current cost ($1.09/meeting) is already very efficient.")
    print("     No immediate optimizations needed unless scaling to 1000s of meetings/day.")
    print()


def main():
    """Run all analyses."""
    print()
    analyze_cost_breakdown()
    analyze_credit_status()
    analyze_quota_capacity()
    analyze_why_credits_unchanged()
    analyze_optimization_opportunities()
    
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                              SUMMARY                                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  ✅ Cost per meeting: ${TOTAL_COST_PER_MEETING:.4f} (very efficient)")
    print(f"  ✅ Meetings remaining: {int(CREDITS_REMAINING / TOTAL_COST_PER_MEETING):,} meetings")
    print(f"  ✅ Quota capacity: 100+ concurrent users supported")
    print(f"  ✅ Credits unchanged: Likely billing delay or free tier coverage")
    print()
    print("  🎯 RECOMMENDATION:")
    print("     Your system is well-optimized and ready for competition.")
    print("     No changes needed. Monitor AWS Billing Console for actual usage.")
    print()


if __name__ == '__main__':
    main()
