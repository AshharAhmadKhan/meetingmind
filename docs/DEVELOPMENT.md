# Development Guide

Complete guide for setting up and developing MeetingMind locally.

**Last Updated:** February 22, 2026

## Prerequisites

### Required Software
- **Node.js**: v18+ (for frontend)
- **Python**: 3.11+ (for backend)
- **AWS CLI**: v2+ (for deployment)
- **AWS SAM CLI**: v1.100+ (for local testing)
- **Git**: v2.30+

### AWS Account Setup
1. Create an AWS account
2. Configure AWS CLI with credentials:
   ```bash
   aws configure
   ```
3. Set default region to `ap-south-1`

## Project Structure

```
meetingmind/
├── backend/              # AWS Lambda functions
│   ├── functions/        # Lambda function code
│   ├── layers/           # Lambda layers
│   ├── template.yaml     # SAM template
│   └── constants.py      # Shared constants
├── frontend/             # React application
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── package.json      # Dependencies
├── scripts/              # Utility scripts
│   ├── deploy-frontend.ps1
│   └── testing/          # Test scripts
└── docs/                 # Documentation
```

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in `backend/`:
```bash
AWS_REGION=ap-south-1
STACK_NAME=meetingmind-dev
AUDIO_BUCKET=meetingmind-audio-dev
MEETINGS_TABLE=meetingmind-meetings-dev
TEAMS_TABLE=meetingmind-teams-dev
```

### 3. Deploy Backend

```bash
# Build
sam build

# Deploy
sam deploy \
  --stack-name meetingmind-dev \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1 \
  --resolve-s3 \
  --no-fail-on-empty-changeset
```

### 4. Local Testing

```bash
# Start local API
sam local start-api --port 3001

# Invoke specific function
sam local invoke ProcessMeetingFunction \
  --event events/s3-event.json

# Generate sample events
sam local generate-event s3 put > events/s3-event.json
```

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create `.env` file in `frontend/`:
```bash
VITE_API_URL=https://your-api-gateway-url.execute-api.ap-south-1.amazonaws.com
VITE_USER_POOL_ID=ap-south-1_xxxxxxxxx
VITE_USER_POOL_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
VITE_REGION=ap-south-1
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

Edit code in `backend/functions/` or `frontend/src/`

### 3. Test Locally

```bash
# Backend
sam local invoke YourFunction --event events/test-event.json

# Frontend
npm run dev
```

### 4. Run Tests

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
npm test
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add your feature"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Common Development Tasks

### Add New Lambda Function

1. Create function directory:
   ```bash
   mkdir backend/functions/your-function
   ```

2. Create `app.py`:
   ```python
   import json
   
   def lambda_handler(event, context):
       return {
           'statusCode': 200,
           'body': json.dumps({'message': 'Hello'})
       }
   ```

3. Add to `template.yaml`:
   ```yaml
   YourFunction:
     Type: AWS::Serverless::Function
     Properties:
       CodeUri: functions/your-function/
       Handler: app.lambda_handler
       Runtime: python3.11
       Events:
         Api:
           Type: Api
           Properties:
             Path: /your-endpoint
             Method: get
   ```

4. Deploy:
   ```bash
   sam build && sam deploy
   ```

### Add New React Component

1. Create component file:
   ```bash
   touch frontend/src/components/YourComponent.jsx
   ```

2. Implement component:
   ```jsx
   export default function YourComponent() {
     return (
       <div>
         <h1>Your Component</h1>
       </div>
     );
   }
   ```

3. Import and use:
   ```jsx
   import YourComponent from './components/YourComponent';
   
   function App() {
     return <YourComponent />;
   }
   ```

### Add New API Endpoint

1. Create Lambda function (see above)

2. Add API Gateway integration in `template.yaml`:
   ```yaml
   Events:
     GetEndpoint:
       Type: Api
       Properties:
         Path: /your-endpoint
         Method: get
         Auth:
           Authorizer: CognitoAuthorizer
   ```

3. Update frontend API client:
   ```javascript
   export async function getYourData() {
     const response = await fetch(`${API_URL}/your-endpoint`, {
       headers: {
         'Authorization': `Bearer ${token}`
       }
     });
     return response.json();
   }
   ```

### Debug Lambda Functions

1. Enable X-Ray tracing in `template.yaml`:
   ```yaml
   Tracing: Active
   ```

2. Add logging:
   ```python
   import logging
   logger = logging.getLogger()
   logger.setLevel(logging.INFO)
   
   logger.info(f"Processing event: {event}")
   ```

3. View logs:
   ```bash
   sam logs -n YourFunction --stack-name meetingmind-dev --tail
   ```

### Test with Real AWS Services

1. Deploy to dev stack:
   ```bash
   sam deploy --stack-name meetingmind-dev
   ```

2. Get API URL:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name meetingmind-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
     --output text
   ```

3. Test endpoint:
   ```bash
   curl https://your-api-url/meetings \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

## Troubleshooting

### Backend Issues

**Issue: SAM build fails**
```bash
# Solution: Clear build cache
rm -rf .aws-sam
sam build --use-container
```

**Issue: Lambda timeout**
```yaml
# Solution: Increase timeout in template.yaml
Timeout: 900  # 15 minutes
```

**Issue: Permission denied**
```yaml
# Solution: Add IAM permissions in template.yaml
Policies:
  - DynamoDBCrudPolicy:
      TableName: !Ref MeetingsTable
```

### Frontend Issues

**Issue: CORS error**
```javascript
// Solution: Add CORS headers in Lambda
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    },
    'body': json.dumps(data)
}
```

**Issue: Build fails**
```bash
# Solution: Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue: Environment variables not loading**
```javascript
// Solution: Restart dev server after changing .env
npm run dev
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use docstrings for functions

```python
def process_meeting(meeting_id: str, user_id: str) -> dict:
    """
    Process a meeting and extract action items.
    
    Args:
        meeting_id: Unique meeting identifier
        user_id: User who uploaded the meeting
        
    Returns:
        dict: Processed meeting data
    """
    pass
```

### JavaScript/React (Frontend)
- Use ES6+ features
- Functional components with hooks
- Use Tailwind CSS for styling
- Max line length: 100 characters

```javascript
export default function MeetingCard({ meeting }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold">{meeting.title}</h3>
    </div>
  );
}
```

## Performance Optimization

### Backend
- Use DynamoDB batch operations
- Enable Lambda function caching
- Optimize cold start times
- Use Lambda layers for shared code

### Frontend
- Code splitting with React.lazy()
- Image optimization
- Minimize bundle size
- Use React.memo for expensive components

## Security Best Practices

1. **Never commit secrets**
   - Use `.env` files (gitignored)
   - Use AWS Secrets Manager for production

2. **Validate all inputs**
   ```python
   if not meeting_id or not isinstance(meeting_id, str):
       raise ValueError("Invalid meeting_id")
   ```

3. **Use least privilege IAM**
   - Only grant necessary permissions
   - Use resource-specific policies

4. **Sanitize user input**
   ```javascript
   const sanitized = DOMPurify.sanitize(userInput);
   ```

## Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
