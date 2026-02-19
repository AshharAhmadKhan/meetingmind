# Deploy All Updated Lambda Functions
# Deploys all 18 Lambda functions with CORS and Decimal fixes

$ErrorActionPreference = "Stop"

Write-Host "=" * 70
Write-Host "Deploying All Lambda Functions with CORS & Decimal Fixes"
Write-Host "=" * 70
Write-Host ""

$functions = @(
    @{Name="GetUploadUrlFunction"; LambdaName="meetingmind-get-upload-url"},
    @{Name="ProcessMeetingFunction"; LambdaName="meetingmind-process-meeting"},
    @{Name="ListMeetingsFunction"; LambdaName="meetingmind-list-meetings"},
    @{Name="GetMeetingFunction"; LambdaName="meetingmind-get-meeting"},
    @{Name="UpdateActionFunction"; LambdaName="meetingmind-update-action"},
    @{Name="GetAllActionsFunction"; LambdaName="meetingmind-get-all-actions"},
    @{Name="CheckDuplicateFunction"; LambdaName="meetingmind-check-duplicate"},
    @{Name="GetDebtAnalyticsFunction"; LambdaName="meetingmind-get-debt-analytics"},
    @{Name="CreateTeamFunction"; LambdaName="meetingmind-create-team"},
    @{Name="JoinTeamFunction"; LambdaName="meetingmind-join-team"},
    @{Name="GetTeamFunction"; LambdaName="meetingmind-get-team"},
    @{Name="ListUserTeamsFunction"; LambdaName="meetingmind-list-user-teams"},
    @{Name="SendRemindersFunction"; LambdaName="meetingmind-send-reminders"},
    @{Name="DailyDigestFunction"; LambdaName="meetingmind-daily-digest"},
    @{Name="SendWelcomeEmailFunction"; LambdaName="meetingmind-send-welcome-email"},
    @{Name="PreSignupFunction"; LambdaName="meetingmind-pre-signup"},
    @{Name="PostConfirmationFunction"; LambdaName="meetingmind-post-confirmation"},
    @{Name="DLQHandlerFunction"; LambdaName="meetingmind-dlq-handler"}
)

$deployed = 0
$failed = 0

foreach ($func in $functions) {
    Write-Host "Deploying $($func.LambdaName)..." -ForegroundColor Cyan
    
    try {
        # Create zip file
        $zipPath = "backend\$($func.Name).zip"
        $sourcePath = "backend\.aws-sam\build\$($func.Name)\*"
        
        Compress-Archive -Path $sourcePath -DestinationPath $zipPath -Force
        
        # Deploy to Lambda
        aws lambda update-function-code `
            --function-name $func.LambdaName `
            --zip-file "fileb://$zipPath" `
            --region ap-south-1 | Out-Null
        
        Write-Host "  ✓ Deployed $($func.LambdaName)" -ForegroundColor Green
        $deployed++
        
        # Clean up zip
        Remove-Item $zipPath -Force
        
    } catch {
        Write-Host "  ✗ Failed to deploy $($func.LambdaName): $_" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Deployment Summary"
Write-Host "=" * 70
Write-Host "✓ Deployed: $deployed / $($functions.Count)" -ForegroundColor Green
if ($failed -gt 0) {
    Write-Host "✗ Failed: $failed / $($functions.Count)" -ForegroundColor Red
}
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Wait 30 seconds for Lambda functions to update"
Write-Host "2. Test frontend at https://dcfx593ywvy92.cloudfront.net"
Write-Host "3. Check CloudWatch logs if issues persist"
Write-Host "=" * 70
