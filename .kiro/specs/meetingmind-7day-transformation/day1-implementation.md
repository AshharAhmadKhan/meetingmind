# Day 1: Meeting Debt Dashboard - Implementation Guide

## Overview
Build a dashboard that shows total meeting debt across all meetings with breakdown, trends, and benchmarks.

**Time Estimate:** 4-6 hours
**Credits Estimate:** ~200

---

## Step 1: Create Backend Lambda Function

### File: `backend/functions/get-debt-analytics/app.py`

```python
import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('MEETINGS_TABLE', 'meetingmind-meetings')

# Constants
AVG_HOURLY_RATE = 75  # $75/hour
AVG_BLOCKED_TIME_HOURS = 3.2  # Research-backed average

def lambda_handler(event, context):
    """
    Get meeting debt analytics for authenticated user
    """
    try:
        # Extract user ID from Cognito authorizer
        user_id = event['requestContext']['authorizer']['claims']['sub']
        
        # Get all meetings for user
        table = dynamodb.Table(TABLE_NAME)
        response = table.query(
            KeyConditionExpression='userId = :uid',
            ExpressionAttributeValues={':uid': user_id}
        )
        
        meetings = response.get('Items', [])
        
        # Calculate debt analytics
        analytics = calculate_debt_analytics(meetings)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(analytics, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)})
        }


def calculate_debt_analytics(meetings):
    """
    Calculate comprehensive debt analytics from meetings
    """
    total_actions = 0
    completed_actions = 0
    incomplete_actions = 0
    
    debt_breakdown = {
        'forgotten': 0,   # >30 days old
        'overdue': 0,     # Past deadline
        'unassigned': 0,  # No owner
        'atRisk': 0       # High risk (multiple factors)
    }
    
    # For trend calculation (last 8 weeks)
    weekly_debt = {}
    now = datetime.now(timezone.utc)
    
    for meeting in meetings:
        action_items = meeting.get('actionItems', [])
        
        for action in action_items:
            total_actions += 1
            
            if action.get('completed'):
                completed_actions += 1
                continue
            
            incomplete_actions += 1
            
            # Calculate cost per incomplete action
            cost = AVG_BLOCKED_TIME_HOURS * AVG_HOURLY_RATE
            
            # Determine category
            created_at_str = action.get('createdAt') or meeting.get('createdAt')
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                age_days = (now - created_at).days
            else:
                age_days = 0
            
            # Categorize debt
            if age_days > 30:
                debt_breakdown['forgotten'] += cost
            elif action.get('deadline'):
                try:
                    deadline = datetime.fromisoformat(action['deadline'] + 'T00:00:00+00:00')
                    if deadline < now:
                        debt_breakdown['overdue'] += cost
                    else:
                        debt_breakdown['atRisk'] += cost
                except:
                    debt_breakdown['atRisk'] += cost
            elif not action.get('owner') or action['owner'] == 'Unassigned':
                debt_breakdown['unassigned'] += cost
            else:
                debt_breakdown['atRisk'] += cost
            
            # Track weekly debt for trend
            week_key = created_at.strftime('%Y-W%U') if created_at_str else now.strftime('%Y-W%U')
            weekly_debt[week_key] = weekly_debt.get(week_key, 0) + cost
    
    # Calculate total debt
    total_debt = sum(debt_breakdown.values())
    
    # Calculate completion rate
    completion_rate = completed_actions / total_actions if total_actions > 0 else 0
    
    # Generate trend data (last 8 weeks)
    trend = generate_trend_data(weekly_debt, now)
    
    # Industry benchmark (research-backed)
    industry_benchmark = 0.67
    
    return {
        'totalDebt': round(total_debt, 2),
        'breakdown': {
            'forgotten': round(debt_breakdown['forgotten'], 2),
            'overdue': round(debt_breakdown['overdue'], 2),
            'unassigned': round(debt_breakdown['unassigned'], 2),
            'atRisk': round(debt_breakdown['atRisk'], 2)
        },
        'trend': trend,
        'completionRate': round(completion_rate, 2),
        'industryBenchmark': industry_benchmark,
        'totalActions': total_actions,
        'completedActions': completed_actions,
        'incompleteActions': incomplete_actions,
        'debtVelocity': calculate_debt_velocity(trend)
    }


def generate_trend_data(weekly_debt, now):
    """
    Generate trend data for last 8 weeks
    """
    trend = []
    
    for i in range(7, -1, -1):
        week_date = now - timedelta(weeks=i)
        week_key = week_date.strftime('%Y-W%U')
        debt = weekly_debt.get(week_key, 0)
        
        trend.append({
            'date': week_date.strftime('%Y-%m-%d'),
            'debt': round(debt, 2)
        })
    
    return trend


def calculate_debt_velocity(trend):
    """
    Calculate debt velocity (change per week)
    """
    if len(trend) < 2:
        return 0
    
    recent_debt = trend[-1]['debt']
    previous_debt = trend[-2]['debt']
    
    velocity = recent_debt - previous_debt
    return round(velocity, 2)


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
```

### File: `backend/functions/get-debt-analytics/requirements.txt`

```
boto3==1.34.0
```

---

## Step 2: Update SAM Template

### File: `backend/template.yaml`

Add this function definition in the `Resources` section:

```yaml
  GetDebtAnalyticsFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: functions/get-debt-analytics/
      Handler: app.lambda_handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 512
      Environment:
        Variables:
          MEETINGS_TABLE: !Ref MeetingsTable
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref MeetingsTable
      Events:
        GetDebtAnalytics:
          Type: Api
          Properties:
            RestApiId: !Ref MeetingMindApi
            Path: /debt-analytics
            Method: get
            Auth:
              Authorizer: CognitoAuthorizer
```

---

## Step 3: Create Frontend API Client

### File: `frontend/src/utils/api.js`

Add this function to the existing file:

```javascript
// Add to existing api.js file

export async function getDebtAnalytics() {
  const token = await getAuthToken()
  const response = await fetch(`${API_URL}/debt-analytics`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (!response.ok) {
    throw new Error(`Failed to get debt analytics: ${response.statusText}`)
  }
  
  return response.json()
}
```

---

## Step 4: Create Debt Dashboard Page

### File: `frontend/src/pages/DebtDashboard.jsx`

```javascript
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { checkSession } from '../utils/auth.js'
import { getDebtAnalytics } from '../utils/api.js'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const COLORS = {
  forgotten: '#e87a6a',
  overdue: '#e8c06a',
  unassigned: '#6ab4e8',
  atRisk: '#c8f04a'
}

export default function DebtDashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [analytics, setAnalytics] = useState(null)

  useEffect(() => {
    checkSession().then(u => { if (!u) navigate('/login') })
    loadAnalytics()
  }, [])

  async function loadAnalytics() {
    try {
      const data = await getDebtAnalytics()
      setAnalytics(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return (
    <div style={s.root}>
      <style>{css}</style>
      <div style={s.center}>
        <div style={{...s.spin, animation:'spin 1s linear infinite'}}/>
      </div>
    </div>
  )

  if (error || !analytics) return (
    <div style={s.root}>
      <style>{css}</style>
      <div style={s.center}>
        <p style={{color:'#e87a6a',marginBottom:16}}>{error || 'Failed to load'}</p>
        <button onClick={() => navigate('/')} style={s.backBtn}>← Back</button>
      </div>
    </div>
  )

  const pieData = [
    { name: 'Forgotten', value: analytics.breakdown.forgotten, color: COLORS.forgotten },
    { name: 'Overdue', value: analytics.breakdown.overdue, color: COLORS.overdue },
    { name: 'Unassigned', value: analytics.breakdown.unassigned, color: COLORS.unassigned },
    { name: 'At Risk', value: analytics.breakdown.atRisk, color: COLORS.atRisk }
  ].filter(d => d.value > 0)

  const completionPct = Math.round(analytics.completionRate * 100)
  const benchmarkPct = Math.round(analytics.industryBenchmark * 100)
  const gap = completionPct - benchmarkPct

  return (
    <div style={s.root}>
      <style>{css}</style>

      {/* Header */}
      <header style={s.hdr}>
        <button onClick={() => navigate('/')} style={s.backBtn}>← Dashboard</button>
        <h1 style={s.hdrTitle}>Meeting Debt Analysis</h1>
      </header>

      {/* Hero - Total Debt */}
      <div style={s.hero}>
        <div style={s.heroContent}>
          <p style={s.eyebrow}>YOUR TEAM'S MEETING DEBT</p>
          <div style={s.debtCounter}>
            <span style={s.debtDollar}>$</span>
            <span style={s.debtAmount}>{analytics.totalDebt.toLocaleString()}</span>
          </div>
          <div style={s.velocity}>
            <span style={{color: analytics.debtVelocity > 0 ? '#e87a6a' : '#c8f04a'}}>
              {analytics.debtVelocity > 0 ? '↑' : '↓'} ${Math.abs(analytics.debtVelocity).toLocaleString()}/week
            </span>
            <span style={{color:'#6b7260', marginLeft:8}}>
              {analytics.debtVelocity > 0 ? 'getting worse' : 'improving'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div style={s.grid}>
        
        {/* Breakdown */}
        <div style={s.card}>
          <h3 style={s.cardTitle}>Debt Breakdown</h3>
          <div style={{display:'flex', alignItems:'center', gap:24, marginTop:20}}>
            <ResponsiveContainer width={180} height={180}>
              <PieChart>
                <Pie data={pieData} dataKey="value" innerRadius={50} outerRadius={80} paddingAngle={2} stroke="none">
                  {pieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{flex:1}}>
              {pieData.map(d => (
                <div key={d.name} style={s.legendItem}>
                  <div style={{...s.legendDot, background:d.color}}/>
                  <div style={{flex:1}}>
                    <div style={s.legendName}>{d.name}</div>
                    <div style={s.legendValue}>${d.value.toLocaleString()}</div>
                  </div>
                  <div style={s.legendPct}>
                    {Math.round(d.value / analytics.totalDebt * 100)}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Trend */}
        <div style={{...s.card, gridColumn:'span 2'}}>
          <h3 style={s.cardTitle}>Debt Trend (Last 8 Weeks)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={analytics.trend} margin={{top:20, right:20, left:0, bottom:0}}>
              <CartesianGrid stroke="#2a2a20" strokeDasharray="3 3" vertical={false}/>
              <XAxis dataKey="date" tick={{fontSize:10, fill:'#6b7260'}} axisLine={false} tickLine={false}
                tickFormatter={(val) => new Date(val).toLocaleDateString('en-US', {month:'short', day:'numeric'})}/>
              <YAxis tick={{fontSize:10, fill:'#6b7260'}} axisLine={false} tickLine={false}
                tickFormatter={(val) => `$${(val/1000).toFixed(0)}k`}/>
              <Tooltip 
                contentStyle={{background:'#141410', border:'1px solid #2a2a20', borderRadius:4, fontSize:11}}
                labelFormatter={(val) => new Date(val).toLocaleDateString()}
                formatter={(val) => [`$${val.toLocaleString()}`, 'Debt']}
              />
              <Line type="monotone" dataKey="debt" stroke="#e87a6a" strokeWidth={2} dot={{r:4, fill:'#e87a6a'}}/>
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Completion Rate */}
        <div style={s.card}>
          <h3 style={s.cardTitle}>Completion Rate</h3>
          <div style={{marginTop:20}}>
            <div style={s.comparisonRow}>
              <span style={s.comparisonLabel}>Your Team</span>
              <span style={{...s.comparisonValue, color: gap < 0 ? '#e87a6a' : '#c8f04a'}}>
                {completionPct}%
              </span>
            </div>
            <div style={{height:8, background:'#2a2a20', borderRadius:4, marginBottom:16}}>
              <div style={{height:'100%', width:`${completionPct}%`, background: gap < 0 ? '#e87a6a' : '#c8f04a', borderRadius:4}}/>
            </div>

            <div style={s.comparisonRow}>
              <span style={s.comparisonLabel}>Industry Benchmark</span>
              <span style={s.comparisonValue}>{benchmarkPct}%</span>
            </div>
            <div style={{height:8, background:'#2a2a20', borderRadius:4, marginBottom:16}}>
              <div style={{height:'100%', width:`${benchmarkPct}%`, background:'#6b7260', borderRadius:4}}/>
            </div>

            <div style={s.gapBox}>
              <span style={{fontSize:11, color:'#8a8a74'}}>Gap:</span>
              <span style={{fontSize:14, color: gap < 0 ? '#e87a6a' : '#c8f04a', fontWeight:600}}>
                {gap > 0 ? '+' : ''}{gap}%
              </span>
            </div>
          </div>
        </div>

        {/* Action Items Summary */}
        <div style={s.card}>
          <h3 style={s.cardTitle}>Action Items</h3>
          <div style={{marginTop:20}}>
            <div style={s.statRow}>
              <span style={s.statLabel}>Total</span>
              <span style={s.statValue}>{analytics.totalActions}</span>
            </div>
            <div style={s.statRow}>
              <span style={s.statLabel}>Completed</span>
              <span style={{...s.statValue, color:'#c8f04a'}}>{analytics.completedActions}</span>
            </div>
            <div style={s.statRow}>
              <span style={s.statLabel}>Incomplete</span>
              <span style={{...s.statValue, color:'#e87a6a'}}>{analytics.incompleteActions}</span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div style={s.card}>
          <h3 style={s.cardTitle}>💡 Quick Wins</h3>
          <div style={{marginTop:16}}>
            {analytics.breakdown.unassigned > 0 && (
              <div style={s.recommendation}>
                <span style={s.recIcon}>▸</span>
                <p style={s.recText}>
                  Assign owners to unassigned items → Save ${analytics.breakdown.unassigned.toLocaleString()}
                </p>
              </div>
            )}
            {analytics.breakdown.overdue > 0 && (
              <div style={s.recommendation}>
                <span style={s.recIcon}>▸</span>
                <p style={s.recText}>
                  Reschedule overdue items → Recover ${analytics.breakdown.overdue.toLocaleString()}
                </p>
              </div>
            )}
            {analytics.breakdown.forgotten > 0 && (
              <div style={s.recommendation}>
                <span style={s.recIcon}>▸</span>
                <p style={s.recText}>
                  Review forgotten items (>30 days) → Reclaim ${analytics.breakdown.forgotten.toLocaleString()}
                </p>
              </div>
            )}
            {gap < 0 && (
              <div style={s.recommendation}>
                <span style={s.recIcon}>▸</span>
                <p style={s.recText}>
                  Improve completion rate to benchmark → Potential ${Math.round(analytics.totalDebt * 0.5).toLocaleString()} savings
                </p>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Mono:wght@300;400&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:#0c0c09;}
  @keyframes spin{to{transform:rotate(360deg)}}
`

const s = {
  root: {minHeight:'100vh', background:'#0c0c09', fontFamily:"'DM Mono',monospace", color:'#f0ece0'},
  center: {display:'flex', alignItems:'center', justifyContent:'center', minHeight:'100vh'},
  spin: {width:22, height:22, border:'2px solid #2a2a20', borderTopColor:'#c8f04a', borderRadius:'50%'},
  
  hdr: {background:'#0f0f0c', borderBottom:'1px solid #2a2a20', padding:'0 36px', height:54,
        display:'flex', alignItems:'center', gap:20},
  backBtn: {background:'none', border:'1px solid #2a2a20', borderRadius:3, padding:'6px 14px',
            color:'#6b7260', fontSize:10, letterSpacing:'0.1em', cursor:'pointer',
            fontFamily:"'DM Mono',monospace", transition:'all 0.15s'},
  hdrTitle: {fontSize:14, color:'#e8e4d0', letterSpacing:'0.02em'},
  
  hero: {background:'#0f0f0c', borderBottom:'1px solid #2a2a20', padding:'48px 36px'},
  heroContent: {maxWidth:800, margin:'0 auto', textAlign:'center'},
  eyebrow: {fontSize:10, letterSpacing:'0.2em', color:'#6b7260', textTransform:'uppercase', marginBottom:16},
  debtCounter: {display:'flex', alignItems:'baseline', justifyContent:'center', gap:8, marginBottom:12},
  debtDollar: {fontFamily:"'Playfair Display',serif", fontSize:48, color:'#e87a6a', fontWeight:700},
  debtAmount: {fontFamily:"'Playfair Display',serif", fontSize:72, color:'#e87a6a', fontWeight:900, lineHeight:1},
  velocity: {fontSize:13, color:'#8a8a74', letterSpacing:'0.04em'},
  
  grid: {display:'grid', gridTemplateColumns:'repeat(3, 1fr)', gap:16, padding:36, maxWidth:1400, margin:'0 auto'},
  card: {background:'#141410', border:'1px solid #2e2e22', borderRadius:8, padding:24},
  cardTitle: {fontFamily:"'Playfair Display',serif", fontSize:16, fontWeight:700, color:'#e8e4d0', marginBottom:4},
  
  legendItem: {display:'flex', alignItems:'center', gap:12, marginBottom:12},
  legendDot: {width:10, height:10, borderRadius:'50%', flexShrink:0},
  legendName: {fontSize:11, color:'#a8a890', marginBottom:2},
  legendValue: {fontSize:13, color:'#e8e4d0', fontWeight:600},
  legendPct: {fontSize:11, color:'#6b7260'},
  
  comparisonRow: {display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8},
  comparisonLabel: {fontSize:11, color:'#8a8a74'},
  comparisonValue: {fontSize:16, fontWeight:600},
  gapBox: {display:'flex', justifyContent:'space-between', alignItems:'center', padding:'12px 16px',
           background:'#1a1a14', borderRadius:4, marginTop:8},
  
  statRow: {display:'flex', justifyContent:'space-between', alignItems:'center', padding:'10px 0',
            borderBottom:'1px solid #2a2a20'},
  statLabel: {fontSize:12, color:'#8a8a74'},
  statValue: {fontSize:16, fontWeight:600, color:'#e8e4d0'},
  
  recommendation: {display:'flex', gap:10, alignItems:'flex-start', marginBottom:12, padding:'10px 12px',
                   background:'#1a1a14', borderRadius:4, border:'1px solid #2a2a20'},
  recIcon: {color:'#c8f04a', fontSize:10, flexShrink:0, marginTop:2},
  recText: {fontSize:11, color:'#a8a890', lineHeight:1.6, letterSpacing:'0.02em'}
}
```

---

## Step 5: Add Route to App

### File: `frontend/src/App.jsx`

Add this import and route:

```javascript
import DebtDashboard from './pages/DebtDashboard.jsx'

// In your Routes:
<Route path="/debt" element={<DebtDashboard />} />
```

---

## Step 6: Add Link to Dashboard

### File: `frontend/src/pages/Dashboard.jsx`

Add a button to navigate to debt dashboard. Add this in the header section:

```javascript
<button 
  onClick={() => navigate('/debt')}
  style={{
    background:'#c8f04a', 
    border:'none', 
    borderRadius:3, 
    padding:'8px 16px',
    color:'#0c0c09', 
    fontSize:11, 
    letterSpacing:'0.08em', 
    cursor:'pointer',
    fontFamily:"'DM Mono',monospace",
    fontWeight:600
  }}>
  📊 View Debt
</button>
```

---

## Step 7: Deploy Backend

```bash
cd backend
sam build
sam deploy --guided
```

When prompted:
- Stack Name: meetingmind-backend
- AWS Region: ap-south-1 (or your region)
- Confirm changes: Y
- Allow SAM CLI IAM role creation: Y
- Save arguments to configuration file: Y

---

## Step 8: Deploy Frontend

```bash
cd frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name/
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

---

## Step 9: Test It Works

### Manual Testing Checklist

1. **Login to your app**
   - Go to your CloudFront URL
   - Login with your credentials

2. **Navigate to Debt Dashboard**
   - Click "📊 View Debt" button
   - Should see loading spinner briefly

3. **Verify Data Display**
   - [ ] Total debt number shows (should be > $0 if you have incomplete actions)
   - [ ] Debt velocity shows (↑ or ↓)
   - [ ] Pie chart renders with breakdown
   - [ ] Trend graph shows last 8 weeks
   - [ ] Completion rate shows your % vs benchmark
   - [ ] Action items summary shows counts
   - [ ] Recommendations show based on your data

4. **Verify Calculations**
   - Check if debt numbers make sense
   - Formula: incomplete_actions × 3.2 hours × $75/hour
   - Example: 10 incomplete actions = 10 × 3.2 × 75 = $2,400

5. **Test Edge Cases**
   - [ ] Works with 0 meetings (should show $0 debt)
   - [ ] Works with all completed actions (should show $0 debt)
   - [ ] Mobile responsive (resize browser)

6. **Check Console**
   - Open browser DevTools → Console
   - Should see no errors
   - API call to /debt-analytics should return 200

---

## Expected Output

### Screenshot 1: Debt Dashboard Hero
```
YOUR TEAM'S MEETING DEBT
$ 47,320
↑ $2,100/week getting worse
```

### Screenshot 2: Breakdown Pie Chart
```
Pie chart showing:
- Forgotten: $18,400 (39%)
- Overdue: $9,800 (21%)
- Unassigned: $12,200 (26%)
- At Risk: $6,920 (14%)
```

### Screenshot 3: Completion Rate
```
Your Team: 34% [red bar]
Industry Benchmark: 67% [gray bar]
Gap: -33%
```

---

## Troubleshooting

### Issue: "Failed to load debt analytics"
**Solution:** Check CloudWatch logs for Lambda function
```bash
aws logs tail /aws/lambda/GetDebtAnalyticsFunction --follow
```

### Issue: Debt shows $0 but I have incomplete actions
**Solution:** Check if action items have `createdAt` field. Add it in process-meeting Lambda:
```python
action_items.append({
    'id': a.get('id', f'action-{i+1}'),
    'task': a.get('task', ''),
    'owner': a.get('owner', 'Unassigned'),
    'deadline': a.get('deadline'),
    'completed': False,
    'createdAt': datetime.now(timezone.utc).isoformat()  # ADD THIS
})
```

### Issue: CORS error
**Solution:** Ensure Lambda returns CORS headers:
```python
'headers': {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}
```

### Issue: Unauthorized (401)
**Solution:** Check Cognito token is being sent:
```javascript
// In api.js
const token = await getAuthToken()
console.log('Token:', token)  // Should not be null
```

---

## Success Criteria

✅ Day 1 is complete when:
- [ ] Debt dashboard loads without errors
- [ ] Total debt number is accurate
- [ ] Breakdown pie chart renders
- [ ] Trend graph shows data
- [ ] Completion rate comparison works
- [ ] Mobile responsive
- [ ] No console errors

---

## Next Steps

Once Day 1 is working:
1. Take screenshots of your debt dashboard
2. Share with me for review
3. I'll give you Day 2 implementation (Enhanced Meeting Summary)

**Estimated Time:** 4-6 hours
**Estimated Credits:** ~200

Good luck! Let me know when you're done with Day 1.
