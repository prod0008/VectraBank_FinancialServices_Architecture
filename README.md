# VectraBank Financial Services Architecture

## Executive Summary
I designed this production deployment architecture for VectraBank's multi-agent financial services application. The design ensures strict regulatory compliance, optimizes model costs by 45%, and establishes clear, actionable operational procedures for the engineering team.

## Architecture Highlights

### 1. Runtime Configuration & Compliance
- **Network Mode**: Configured for VPC isolation in production (PUBLIC for lab)
- **Guardrails**: Financial compliance guardrail (gr-vectrabank-compliance v1) applied to all model calls
- **Audit Trail**: 10% X-Ray tracing sampling rate to satisfy financial audit requirements without prohibitive costs

### 2. Multi-Agent Cost Optimization
Strategic model routing saves ~$4,000/month compared to a single-premium-model approach:

| Agent | Model | Purpose | Monthly Cost |
|-------|-------|---------|--------------|
| Query Router | Amazon Nova Lite | Classify and route queries | $19.80 |
| Market Data Retriever | Amazon Nova Lite | Extract real-time market data | $19.80 |
| Compliance Retriever | Amazon Nova Lite | Lookup regulatory rules | $7.92 |
| Financial Advisor | Claude Sonnet 4.5 | Synthesize complex financial advice | $4,680.00 |

### 3. Monitoring & Observability
- **Dashboard**: 6 essential widgets (Queries, Latency P50/P99, Error Rate, Guardrail Blocks, RAG Quality, Kill Switch Status)
- **Critical Alarms**: 
  - High Error Rate (> 2% over 5 mins)
  - High Latency P99 (> 8 seconds)
  - Guardrail Violation Spike (> 50 blocks in 5 mins)

### 4. Infrastructure Cost Breakdown
- **Total Estimated Monthly Cost**: $4,912.02
- Includes optimized DynamoDB provisioning, 3 Knowledge Bases, CloudWatch metrics/logs, X-Ray tracing, and VPC networking.

### 5. Operational Runbooks
Clear, step-by-step procedures for the engineering team:
1. **Production Deployment** (15 mins): Staging validation, guardrail check, smoke tests, monitoring.
2. **Emergency Rollback** (10 mins): Identify stable version, revert, verify, post-incident review.
3. **Kill Switch Activation** (5 mins): PagerDuty acknowledgment, X-Ray/CloudWatch investigation, human-approved shutdown, compliance notification.
4. **High Latency Investigation** (20 mins): X-Ray service map analysis, per-agent metrics, bottleneck identification, scaling.

## Setup & Usage

Clone the repository and install dependencies:

    git clone https://github.com/prod0008/VectraBank_FinancialServices_Architecture.git
    cd VectraBank_FinancialServices_Architecture
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python vectrabank_architecture.py

## Key Takeaways
1. **Compliance First**: VPC network mode, strict 2% error thresholds, and mandatory human approval for kill switches.
2. **Cost-Aware Design**: Lightweight models for deterministic tasks (routing/retrieval), premium models for complex reasoning (synthesis).
3. **Operational Maturity**: Documented runbooks ensure consistent, rapid response to production incidents.

---
