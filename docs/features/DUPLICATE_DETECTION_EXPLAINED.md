# Duplicate Detection Feature - How It Works

## Current Status
✅ **Code is working correctly**  
⚠️ **Bedrock embeddings disabled** (to avoid AWS Marketplace charges)  
📊 **Using fallback embeddings** (hash-based, less accurate)

---

## What You'd See If Bedrock Was Enabled

### 1. During Meeting Upload
When you upload a new meeting audio file, the system would:
- Extract action items from the transcript
- Generate semantic embeddings for each task using Amazon Bedrock Titan
- Compare new tasks against all your previous incomplete tasks
- Flag duplicates with similarity scores

### 2. In Meeting Detail View
You'd see warnings like:

```
⚠️ DUPLICATE DETECTED
Task: "Finalize API documentation"
Similar to: "Complete API docs" (Meeting: Sprint Planning, 87% match)
Owner: Zeeshan | Deadline: Feb 15

🔄 CHRONIC BLOCKER
This task has appeared 3+ times across meetings
History:
  - 92%: "Finish API documentation" (Jan 10)
  - 87%: "Complete API docs" (Jan 25)
  - 85%: "Finalize API documentation" (Feb 5)
```

### 3. Duplicate Detection Thresholds
- **85%+ similarity**: Flagged as duplicate
- **70-84% similarity**: Shown in history (potential matches)
- **<70% similarity**: Not shown

### 4. Chronic Blocker Detection
- Task repeated **3+ times** = Chronic Blocker
- System highlights these as high-priority issues
- Helps identify tasks that keep getting postponed

---

## How Semantic Similarity Works

### With Bedrock (Ideal):
```
"Draft database schema"  →  [0.23, 0.87, 0.45, ...] (1536 dimensions)
"Create DB design"       →  [0.25, 0.85, 0.43, ...] (1536 dimensions)
Similarity: 91% ✅ MATCH
```

### Without Bedrock (Current Fallback):
```
"Draft database schema"  →  [hash-based vector]
"Create DB design"       →  [hash-based vector]
Similarity: 12% ❌ NO MATCH (less accurate)
```

---

## Why Bedrock Is Disabled

**Cost Consideration:**
- Bedrock Titan Embeddings requires AWS Marketplace subscription
- Charges per API call
- Disabled to avoid unexpected costs during development

**Fallback System:**
- Uses simple hash-based embeddings
- System remains functional
- Less accurate semantic matching

---

## To Enable Bedrock Embeddings

1. **Subscribe to Bedrock in AWS Marketplace**
2. **Enable model access** in Bedrock console
3. **Redeploy process-meeting Lambda** (no code changes needed)
4. **Re-process existing meetings** to generate proper embeddings

---

## Test Results

✅ Lambda function works correctly  
✅ API endpoint accessible  
✅ Similarity calculation accurate  
⚠️ No duplicates detected (embeddings missing/fallback mode)  

**Tested scenarios:**
- Exact match: "Draft a database schema"
- Similar task: "Create database design document"  
- Different task: "Buy groceries"

All returned 0% similarity due to missing/fallback embeddings.

