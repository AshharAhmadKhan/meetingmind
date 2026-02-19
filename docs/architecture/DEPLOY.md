# MeetingMind Deployment Guide

Quick reference for deploying MeetingMind to AWS.

---

## Frontend Deployment

### Windows (PowerShell)
```powershell
.\deploy-frontend.ps1
```

### Linux/Mac (Bash)
```bash
bash deploy-frontend.sh
```

### Manual Deployment (Any Platform)
```bash
# 1. Build
cd frontend
npm run build

# 2. Upload to S3
aws s3 sync dist/ s3://meetingmind-frontend-707411439284 --delete --region ap-south-1

# 3. Invalidate CloudFront
aws cloudfront create-invalidation --distribution-id E3CAAI97MXY83V --paths "/*"
```

---

## Backend Deployment

### Deploy Backend Stack
```bash
cd backend
sam build
sam deploy
```

### Deploy with Guided Mode (First Time)
```bash
cd backend
sam build
sam deploy --guided
```

---

## Full Stack Deployment

### Windows
```powershell
# Backend
cd backend
sam build
sam deploy
cd ..

# Frontend
.\deploy-frontend.ps1
```

### Linux/Mac
```bash
# Backend
cd backend
sam build
sam deploy
cd ..

# Frontend
bash deploy-frontend.sh
```

---

## Deployment URLs

- **Frontend:** https://dcfx593ywvy92.cloudfront.net
- **API Gateway:** https://25g9jf8sqa.execute-api.ap-south-1.amazonaws.com/prod
- **Debt Dashboard:** https://dcfx593ywvy92.cloudfront.net/debt
- **Region:** ap-south-1 (Mumbai)

---

## Post-Deployment Verification

After deployment, test:
1. Login/signup flow
2. Upload meeting audio
3. View dashboard
4. Kanban board drag-and-drop
5. Team features
6. Debt analytics

---

## Troubleshooting

### CloudFront Cache Not Updating
Wait 1-2 minutes for invalidation to complete, or check status:
```bash
aws cloudfront get-invalidation --distribution-id E3CAAI97MXY83V --id <INVALIDATION_ID>
```

### Build Fails
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### AWS CLI Not Found
Install AWS CLI v2: https://aws.amazon.com/cli/

### SAM Build Fails
```bash
cd backend
sam validate
sam build --use-container
```

---

**Last Updated:** February 19, 2026 - 5:17 PM IST
