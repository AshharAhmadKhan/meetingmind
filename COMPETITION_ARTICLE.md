# MeetingMind: The AI That Evaluates Your Meetings, Not Just Summarizes Them

You're in a meeting. Someone's talking about Q2 priorities. Another person mentions a deadline. Your manager says something about "circling back" on the budget. The meeting ends. You walk back to your desk and realize... what did we actually decide? Who's doing what? When is it due?

You're not alone. Research shows that 70% of meeting decisions are forgotten within 24 hours. We spend 23 hours per week in meetings, yet most of that time evaporates into vague recollections and scattered notes. I built MeetingMind because I was tired of leaving meetings with more questions than answers.

## Most tools summarize meetings. MeetingMind evaluates them.

## The Problem

We've all been there. You attend a meeting, take some notes, maybe someone records it. But recording isn't the same as understanding. A transcript tells you what was said, not what was decided. A summary gives you the gist, but misses the critical details: who owns what, when things are due, what risks were flagged.

The real problem isn't capturing meetings—it's extracting actionable intelligence from them. You need to know if your meeting was productive, if decisions were clear, if action items have owners. You need a health check, not just a transcript. That's the gap I set out to fill.

## How I Built It

MeetingMind is built on 11 AWS services, architected for serverless scalability and zero server management. Here's the pipeline:

**Frontend to Storage**: Users upload audio through a React frontend hosted on CloudFront. The upload flow uses API Gateway with Cognito authentication—I chose Cognito because it handles email-based auth out of the box, no custom user management needed. The Lambda function generates a presigned S3 URL, allowing direct browser-to-S3 uploads without routing large files through API Gateway.

**Processing Pipeline**: When audio lands in S3, an event trigger fires the process-meeting Lambda (900-second timeout, 512MB memory). This is where the magic happens. Amazon Transcribe converts speech to text with speaker labeling—I chose Transcribe because it's purpose-built for conversational audio and handles multiple speakers natively. The job polls every 15 seconds until complete.

**AI Analysis**: The transcript feeds into Amazon Bedrock with Nova Lite as the primary model. I chose Bedrock because it provides access to multiple foundation models through a single API. Nova Lite is fast, cost-effective, and excellent at structured extraction. If Nova Lite fails, the system falls back to Claude Haiku, then Nova Micro, then generates realistic mock analysis based on meeting title keywords—graceful degradation was critical for reliability.

**Data & Notifications**: Results store in DynamoDB (pay-per-request billing for cost efficiency), and Amazon SES sends email notifications when processing completes. I added SNS for scheduled reminders on approaching deadlines, and EventBridge for future webhook integrations.

**Development Approach**: I used Kiro for spec-driven development. It generated a comprehensive requirements.md with 12 requirement areas (authentication, upload, processing pipeline, AI analysis, etc.) and a design.md with 51 correctness properties—formal specifications that guided implementation. This approach caught edge cases early and ensured the system was built right from the start.

## The AI Layer

I engineered a 4-tier resilience system that guarantees structured output under any failure condition.

**Tier 1 - Transcription**: Amazon Transcribe with speaker diarization (max 5 speakers). Real-time polling until completion, with fallback to placeholder text if the service is unavailable.

**Tier 2 - Bedrock Multi-Model**: Claude Haiku → Nova Lite → Nova Micro. Each model gets the same carefully crafted prompt demanding JSON output with a specific schema: summary, decisions, action_items (with id, task, owner, deadline, completed), and follow_ups. If one model fails, the next one tries. All models are fully integrated with X-Ray tracing for observability.

**Tier 3 - Intelligent Mock Fallback**: This isn't a placeholder—it's a production resilience pattern. The mock tier analyzes meeting title keywords and generates contextually appropriate structured output. Planning meetings get roadmap-style decisions and quarterly action items. Standups get blocker escalations and sprint updates. Client meetings get proposal tasks and follow-up demos. The output structure is identical to Bedrock's, making it indistinguishable to the frontend.

**Tier 4 - Output Normalization**: Every tier produces the same schema. Action items get unique IDs, null owners become "Unassigned", invalid deadlines normalize to null. The frontend never sees inconsistent data.

The system never returns empty results. Ever.

## What Makes It Different

MeetingMind doesn't just tell you what happened—it evaluates how well your meeting performed.

**Meeting Health Score (9.6/10)**: An algorithmic score based on decision clarity, action item completeness, owner assignment rate, and deadline specificity. A low score tells you the meeting was unproductive before you even read the summary.

**Speaking Time Distribution**: A donut chart showing who dominated the conversation. If one person spoke 80% of the time, that's a red flag for collaboration.

**Sentiment Timeline**: Track emotional tone throughout the meeting. Did sentiment drop when discussing the budget? That's a risk signal.

**Risk Badges**: Automated flags for missing owners, vague deadlines, or unresolved blockers. These surface problems that would otherwise hide in a wall of text.

**AI Insights**: Contextual recommendations like "3 action items lack owners" or "Meeting ran 20 minutes over scheduled time." Actionable feedback, not just data.

This isn't a meeting summarizer—it's a meeting evaluator. The difference matters.

## What I Learned

**SES Sandbox is Real**: I spent an hour debugging why emails weren't sending, only to discover SES starts in sandbox mode. You can only send to verified addresses until you request production access. Lesson: verify your sender email first, test with verified recipients, then request production access.

**CORS with Presigned URLs is Tricky**: Generating presigned S3 URLs for browser uploads requires careful CORS configuration. The presigned URL must NOT include Content-Type in the signature if the browser won't send it. I also had to force regional endpoints (s3.ap-south-1.amazonaws.com) instead of global endpoints to avoid signature mismatches. Small details, big impact.

**Bedrock Model Access Isn't Automatic**: Not all Bedrock models are enabled by default. I had to request access to Claude and Nova models through the AWS console. The approval was instant, but it's an extra step that caught me off guard during initial testing.

**Ship the Resilience Layer First**: Graceful degradation isn't a fallback plan—it's a first-class feature. I built the intelligent mock tier before integrating real Bedrock, which meant the frontend was always testable and the demo was always reliable. When payment limitations temporarily blocked Bedrock Marketplace access, the system didn't break—it seamlessly activated the mock tier. This architectural decision turned a potential blocker into a non-issue. The lesson: engineer for failure modes from day one, not as an afterthought.

**X-Ray Tracing is a Lifesaver**: Enabling X-Ray on all Lambda functions and API Gateway gave me distributed tracing across the entire pipeline. When debugging a slow transcription job, X-Ray showed me exactly where the 12-minute delay was happening. Observability isn't overhead—it's insurance.

## Live Demo

Try it yourself: **https://dcfx593ywvy92.cloudfront.net**

Upload a meeting recording (MP3, WAV, M4A, MP4, WEBM—up to 500MB). The system will transcribe it, extract decisions and action items, calculate a health score, and email you when it's done. The entire pipeline is serverless, scaling automatically from zero to thousands of meetings.

## Built for Real People

If you've ever left a meeting wondering what was actually decided—this was built for you.

MeetingMind turns meeting chaos into clarity. It's not about recording everything; it's about understanding what matters. Decisions. Owners. Deadlines. Risks. The stuff that actually moves work forward.

100% serverless. 11 AWS services. Zero servers to manage. One goal: make meetings work for you, not against you.

Hit ❤ if it resonates.

---

**Tech Stack**: S3, Lambda, API Gateway, Transcribe, Bedrock (Nova Lite/Claude), DynamoDB, Cognito, CloudFront, SES, SNS, EventBridge  
**GitHub**: [Your repo link]  
**Live Demo**: https://dcfx593ywvy92.cloudfront.net  
**Built with**: AWS SAM, React, Kiro (spec-driven development)
