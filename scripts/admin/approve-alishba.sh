#!/bin/bash
# Quick script to approve Alishba's account

EMAIL="alishba@jamiahamdard.org.in"
USER_POOL_ID="ap-south-1_YourPoolId"  # Update with actual pool ID
REGION="ap-south-1"

echo "Approving user: $EMAIL"

# Admin confirm signup
aws cognito-idp admin-confirm-sign-up \
    --user-pool-id $USER_POOL_ID \
    --username $EMAIL \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ User confirmed successfully"
    
    # Set email as verified
    aws cognito-idp admin-update-user-attributes \
        --user-pool-id $USER_POOL_ID \
        --username $EMAIL \
        --user-attributes Name=email_verified,Value=true \
        --region $REGION
    
    if [ $? -eq 0 ]; then
        echo "✅ Email verified successfully"
        echo ""
        echo "User $EMAIL is now approved and can log in!"
    else
        echo "⚠️  User confirmed but email verification failed"
    fi
else
    echo "❌ Failed to confirm user"
    echo "Make sure:"
    echo "  1. The user has completed signup"
    echo "  2. USER_POOL_ID is correct"
    echo "  3. AWS credentials are configured"
fi
