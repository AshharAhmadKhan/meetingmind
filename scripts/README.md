# MeetingMind Scripts

Utility scripts for deployment, testing, and data management.

## 🚀 Deployment Scripts

### Quick Deploy
```bash
# Deploy everything (backend + frontend)
.\deploy-all.ps1          # Windows
bash deploy-all.sh        # Linux/Mac

# Deploy backend only
.\deploy-backend.ps1      # Windows
bash deploy-backend.sh    # Linux/Mac

# Deploy frontend only
.\deploy-frontend.ps1     # Windows
bash deploy-frontend.sh   # Linux/Mac
```

## 🧪 Testing Scripts

### API Testing
- `testing/test-rate-limiting.py` - Test API rate limits
- `testing/test-graveyard-resurrection.py` - Test graveyard feature
- `testing/test-get-meeting-lambda.py` - Test meeting retrieval
- `testing/test-update-action-lambda.py` - Test action updates

### Integration Testing
- `testing/features/` - Feature-specific test scripts
- `testing/core/` - Core functionality tests

## 🔧 Utility Scripts

### Meeting Management
- `trigger-processing.py` - Manually trigger meeting processing
- `check-meeting-status.py` - Check meeting processing status
- `regenerate-autopsies-rulebased.py` - Regenerate meeting autopsies

### Data Management
- `fix-duplicate-action-ids.py` - Fix duplicate action IDs (one-time migration)
- `data/seed-v1-historical.py` - Seed historical data

### Monitoring
- `check-aws-credits.py` - Check AWS credit balance
- `check-user-logs.py` - View user activity logs
- `check-graveyard-data.py` - Inspect graveyard items

### Debugging
- `diagnose-403-error.py` - Debug 403 authorization errors
- `test-cors-fix.sh` - Test CORS configuration
- `verify-kanban-fix.py` - Verify Kanban drag-and-drop fix
- `verify-resurrection.py` - Verify graveyard resurrection

## 📁 Directory Structure

```
scripts/
├── deploy-all.{sh|ps1}           # Deploy everything
├── deploy-backend.{sh|ps1}       # Deploy backend
├── deploy-frontend.{sh|ps1}      # Deploy frontend
├── data/                         # Data management scripts
├── deploy/                       # Legacy deploy scripts
├── setup/                        # Setup and configuration
└── testing/                      # Test scripts
    ├── features/                 # Feature tests
    └── core/                     # Core tests
```

## 🔐 Configuration

All scripts use these AWS resources:
- **Stack:** meetingmind-stack
- **Region:** ap-south-1
- **S3 Frontend:** meetingmind-frontend-707411439284
- **CloudFront:** E3CAAI97MXY83V
- **API:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod

## 📝 Usage Examples

### Deploy after code changes
```bash
# Backend code changed
.\deploy-backend.ps1

# Frontend code changed
.\deploy-frontend.ps1

# Both changed
.\deploy-all.ps1
```

### Test API rate limiting
```bash
python testing/test-rate-limiting.py
```

### Check meeting processing
```bash
python check-meeting-status.py <meeting-id>
```

### Manually process a meeting
```bash
python trigger-processing.py <meeting-id>
```

## ⚠️ Important Notes

1. **Deployment scripts** require AWS CLI configured with proper credentials
2. **Test scripts** may require authentication tokens (see script comments)
3. **Data scripts** should be run carefully in production
4. **One-time scripts** (like fix-duplicate-action-ids.py) should only be run once

## 🆘 Troubleshooting

### Script fails with "command not found"
- Ensure AWS CLI is installed: `aws --version`
- Ensure SAM CLI is installed: `sam --version`
- Ensure Node.js is installed: `node --version`

### Permission denied on Linux/Mac
```bash
chmod +x deploy-*.sh
```

### PowerShell execution policy error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📚 More Information

See [DEPLOYMENT.md](../DEPLOYMENT.md) for detailed deployment guide.
