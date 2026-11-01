"""
vectrabank_architecture.py - EXERCISE STARTER (Student-Led)
==============================================================
Module 10 Exercise: Plan a Production Deployment Architecture for VectraBank

Create a deployment architecture plan for VectraBank's financial services
multi-agent system. Define runtime configuration, monitoring strategy,
cost estimates, and operational runbooks.

Same planning pattern as the demo (deployment_walkthrough.py),
with additions:
  1. FINANCIAL DOMAIN — VectraBank-specific agents and KBs
  2. OPERATIONAL RUNBOOK (NEW) — deploy, rollback, kill switch, latency
  3. COMPLIANCE REQUIREMENTS — VPC network mode, stricter thresholds
  4. COST OPTIMIZATION — model selection recommendations

Instructions:
  - Follow the demo pattern (deployment_walkthrough.py)
  - Look for TODO 1-8 below
  - Define configs as Python dicts (no AWS calls needed)
  - Focus on WHAT to configure and WHY
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()


# ═══════════════════════════════════════════════════════
#  VECTRABANK RUNTIME CONFIGURATION
# ═══════════════════════════════════════════════════════

# TODO 1: Define the AgentCore Runtime configuration
VECTRABANK_RUNTIME_CONFIG = {
    "agentRuntimeName": "vectrabank-financial-services",
    "networkMode": "PUBLIC",  # Lab uses PUBLIC. Production would use "VPC".
    # Production VPC Documentation:
    # In a production financial services deployment, networkMode would be "VPC".
    # vpcConfiguration: {
    #     "vpcId": "vpc-0123456789abcdef0",
    #     "subnetIds": ["subnet-private-1a", "subnet-private-1b"], # Private subnets only
    #     "securityGroupIds": ["sg-0abcdef1234567890"] # Restricts outbound to AWS services via VPC endpoints
    # }
    "guardrailIdentifier": os.getenv("GUARDRAIL_ID", "gr-vectrabank-compliance"),
    "guardrailVersion": os.getenv("GUARDRAIL_VERSION", "1"),
    "environmentVariables": {
        "MARKET_DATA_KB_ID": os.getenv("MARKET_DATA_KB_ID", "kb-market-data-placeholder"),
        "COMPLIANCE_KB_ID": os.getenv("COMPLIANCE_KB_ID", "kb-compliance-placeholder"),
        "RISK_ASSESSMENT_KB_ID": os.getenv("RISK_ASSESSMENT_KB_ID", "kb-risk-placeholder"),
        "STATE_TABLE_NAME": os.getenv("STATE_TABLE_NAME", "vectrabank-agent-state"),
        "AUDIT_TABLE_NAME": os.getenv("AUDIT_TABLE_NAME", "vectrabank-audit-logs"),
        "GUARDRAIL_ID": os.getenv("GUARDRAIL_ID", "gr-vectrabank-compliance"),
        "GUARDRAIL_VERSION": os.getenv("GUARDRAIL_VERSION", "1"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-east-1"),
        "LOG_LEVEL": "INFO"
    }
}


# ═══════════════════════════════════════════════════════
#  AGENT DEFINITIONS
# ═══════════════════════════════════════════════════════

# TODO 2: Define 4 agents for VectraBank
VECTRABANK_AGENTS = [
    {
        "name": "QueryRouter",
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.1,
        "role": "Route user queries to the appropriate specialized agent",
        "tools": [],
        "estimated_tokens_per_request": 500,
        "requests_per_day": 10000
    },
    {
        "name": "MarketDataRetriever",
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.0,
        "role": "Retrieve and summarize real-time market data",
        "tools": ["kb_market_data"],
        "estimated_tokens_per_request": 1000,
        "requests_per_day": 5000
    },
    {
        "name": "ComplianceRetriever",
        "model": "amazon.nova-lite-v1:0",
        "temperature": 0.0,
        "role": "Retrieve compliance and regulatory information",
        "tools": ["kb_compliance"],
        "estimated_tokens_per_request": 1000,
        "requests_per_day": 2000
    },
    {
        "name": "FinancialAdvisor",
        "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
        "temperature": 0.3,
        "role": "Synthesize financial advice based on retrieved data and compliance rules",
        "tools": ["kb_risk_assessment"],
        "estimated_tokens_per_request": 2000,
        "requests_per_day": 10000
    }
]


# ═══════════════════════════════════════════════════════
#  MONITORING STRATEGY
# ═══════════════════════════════════════════════════════

# TODO 3, 4, 5: Define the monitoring dashboard, alarms, and X-Ray tracing
VECTRABANK_MONITORING = {
    "dashboard_name": "vectrabank-financial-services",
    "widgets": [
        {"name": "Total Queries", "type": "metric", "metric": "Invocations", "stat": "Sum"},
        {"name": "Latency P50/P99", "type": "metric", "metric": "Latency", "stat": "p50, p99"},
        {"name": "Error Rate", "type": "metric", "metric": "Errors", "stat": "Average", "threshold": 0.02},
        {"name": "Guardrail Blocks", "type": "metric", "metric": "GuardrailInterventions", "stat": "Sum"},
        {"name": "RAG Quality", "type": "metric", "metric": "KnowledgeBaseHits", "stat": "Average"},
        {"name": "Kill Switch Status", "type": "metric", "metric": "KillSwitchActive", "stat": "Maximum"}
    ],
    "alarms": [
        {"name": "HighErrorRate", "metric": "Errors", "threshold": 2.0, "comparison": "GreaterThanThreshold", "period": 300, "evaluation_periods": 2},
        {"name": "HighLatencyP99", "metric": "Latency", "statistic": "p99", "threshold": 8000, "comparison": "GreaterThanThreshold", "period": 300, "evaluation_periods": 2},
        {"name": "GuardrailViolationSpike", "metric": "GuardrailInterventions", "threshold": 50, "comparison": "GreaterThanThreshold", "period": 300, "evaluation_periods": 1}
    ],
    "xray_tracing": {
        "enabled": True,
        "sampling_rate": 0.10,  # 10% for financial audit
        "annotations": ["query_type", "agent_name", "kb_id", "user_id"],
        "metadata": ["transaction_id", "compliance_check_passed"]
    }
}


# ═══════════════════════════════════════════════════════
#  COST ESTIMATION (provided — same as demo)
# ═══════════════════════════════════════════════════════

MODEL_PRICING = {
    "amazon.nova-lite-v1:0": {"input": 0.00006, "output": 0.00024},
    "amazon.nova-pro-v1:0": {"input": 0.0008, "output": 0.0032},
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": {"input": 0.003, "output": 0.015},
}


def estimate_monthly_costs(agents: list, days: int = 30) -> dict:
    """Estimate monthly costs for VectraBank."""
    costs = {}
    total = 0

    for agent in agents:
        model = agent["model"]
        pricing = MODEL_PRICING.get(model, {"input": 0.001, "output": 0.005})
        tokens = agent["estimated_tokens_per_request"]
        daily_requests = agent["requests_per_day"]

        input_tokens = tokens * 0.6
        output_tokens = tokens * 0.4
        daily_cost = ((input_tokens / 1000) * pricing["input"] +
                      (output_tokens / 1000) * pricing["output"]) * daily_requests
        monthly_cost = daily_cost * days

        costs[agent["name"]] = {
            "model": model, "daily_requests": daily_requests,
            "monthly_cost": round(monthly_cost, 2),
        }
        total += monthly_cost

    # TODO 6: Add infrastructure costs
    infrastructure_costs = {
        "dynamodb": {
            "table_state": 15.50,  # Provisioned capacity for agent state
            "table_audit": 12.00,  # Provisioned capacity for compliance audit logs
        },
        "knowledge_bases": {
            "market_data_kb": 25.00,  # Vector storage + retrieval for market data
            "compliance_kb": 20.00,   # Vector storage + retrieval for compliance rules
            "risk_assessment_kb": 25.00,  # Vector storage + retrieval for risk models
        },
        "cloudwatch": {
            "logs": 10.00,  # Log ingestion and storage
            "metrics": 5.00,  # Custom metrics for agents
            "dashboard": 3.00,  # Dashboard hosting
        },
        "xray": {
            "sampling_and_analysis": 15.00,  # 10% sampling rate + trace storage
        },
        "vpc": {
            "nat_gateway": 32.40,  # NAT gateway for outbound traffic
            "vpc_endpoints": 21.60,  # Interface endpoints for Bedrock, S3, DynamoDB
        },
    }

    # TODO 6l: Calculate total infrastructure costs and add to costs dict
    costs["DynamoDB"] = {"monthly_cost": round(sum(infrastructure_costs["dynamodb"].values()), 2)}
    costs["Knowledge Bases"] = {"monthly_cost": round(sum(infrastructure_costs["knowledge_bases"].values()), 2)}
    costs["CloudWatch"] = {"monthly_cost": round(sum(infrastructure_costs["cloudwatch"].values()), 2)}
    costs["X-Ray"] = {"monthly_cost": round(sum(infrastructure_costs["xray"].values()), 2)}
    costs["VPC Networking"] = {"monthly_cost": round(sum(infrastructure_costs["vpc"].values()), 2)}

    infra_total = sum(
        cost for category in infrastructure_costs.values()
        for cost in category.values()
    )
    total += infra_total

    costs["TOTAL"] = {"monthly_cost": round(total, 2)}
    return costs


# ═══════════════════════════════════════════════════════
#  OPERATIONAL RUNBOOK (NEW — not in demo)
# ═══════════════════════════════════════════════════════

# TODO 7: Define 4 operational runbook procedures
OPERATIONAL_RUNBOOK = {
    "deploy": {
        "name": "Production Deployment",
        "steps": [
            "1. Run full integration and unit test suite in staging environment.",
            "2. Validate guardrail configuration and version compatibility.",
            "3. Deploy new runtime version using AgentCore CLI.",
            "4. Run smoke tests on 10 test transactions across all agent paths.",
            "5. Monitor error rate and latency for 5 minutes to ensure stability."
        ],
        "rollback_trigger": "Error rate > 2% or P99 latency > 8s during smoke test",
        "estimated_duration_minutes": 15,
    },

    "rollback": {
        "name": "Emergency Rollback",
        "steps": [
            "1. Identify previous stable runtime version from deployment history.",
            "2. Revert runtime to previous version using AgentCore CLI.",
            "3. Verify agents are responding to transactions and returning expected outputs.",
            "4. Conduct post-incident review to determine root cause of failure."
        ],
        "estimated_duration_minutes": 10,
    },

    "kill_switch": {
        "name": "Kill Switch Activation",
        "steps": [
            "1. Acknowledge alert in PagerDuty and notify on-call engineer.",
            "2. Check AWS X-Ray for error patterns or anomalous request spikes.",
            "3. Check CloudWatch audit logs for guardrail violations or fraud indicators.",
            "4. Disable runtime via AgentCore CLI if attack or fraud is confirmed.",
            "5. Notify compliance and security teams immediately."
        ],
        "threshold": "Guardrail blocks > 50 in 5 minutes",
        "requires_approval": True,  # Financial system requires human approval
        "estimated_duration_minutes": 5,
    },

    "latency_investigation": {
        "name": "High Latency Investigation",
        "steps": [
            "1. Pull X-Ray service map to identify the slowest service or segment.",
            "2. Check per-agent latency metrics in CloudWatch dashboards.",
            "3. Identify bottleneck - is it the LLM agent, KB retrieval, or tool execution?",
            "4. Check DynamoDB throttling events or Knowledge Base retrieval latency.",
            "5. Scale the bottleneck component (e.g., increase provisioned capacity or optimize prompts)."
        ],
        "trigger_threshold": "P99 latency > 8 seconds",
        "estimated_duration_minutes": 20,
    },
}


# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  VectraBank Deployment Architecture — Module 10 Exercise")
    print("  Runtime Config + Monitoring + Cost + Operational Runbook")
    print("=" * 70)

    # ── Runtime Configuration ──
    print(f"\n{'━' * 70}")
    print("  1. AgentCore Runtime Configuration")
    print(f"{'━' * 70}")
    print(f"  {'Parameter':<25s} {'Value':<40s}")
    print(f"  {'─' * 65}")
    print(f"  {'Runtime Name':<25s} {VECTRABANK_RUNTIME_CONFIG['agentRuntimeName']:<40s}")
    print(f"  {'Network Mode':<25s} {VECTRABANK_RUNTIME_CONFIG['networkMode']:<40s}")
    print(f"  {'Guardrail ID':<25s} {VECTRABANK_RUNTIME_CONFIG['guardrailIdentifier']:<40s}")
    print(f"  {'Guardrail Version':<25s} {VECTRABANK_RUNTIME_CONFIG['guardrailVersion']:<40s}")

    # ── Agent Definitions ──
    print(f"\n{'━' * 70}")
    print("  2. Agent Definitions")
    print(f"{'━' * 70}")
    print(f"  {'Agent Name':<25s} {'Model':<40s} {'Temp':>5s}")
    print(f"  {'─' * 70}")
    for agent in VECTRABANK_AGENTS:
        print(f"  {agent['name']:<25s} {agent['model']:<40s} {agent['temperature']:>5.1f}")

    # ── Monitoring Strategy ──
    print(f"\n{'━' * 70}")
    print("  3. Monitoring Strategy")
    print(f"{'━' * 70}")
    print(f"  Dashboard: {VECTRABANK_MONITORING['dashboard_name']}")
    print(f"  X-Ray Sampling Rate: {VECTRABANK_MONITORING['xray_tracing']['sampling_rate'] * 100:.0f}%")
    print(f"\n  {'Widget / Alarm':<30s} {'Type / Threshold':<35s}")
    print(f"  {'─' * 65}")
    for widget in VECTRABANK_MONITORING['widgets']:
        print(f"  {widget['name']:<30s} {'Widget: ' + widget['type']:<35s}")
    for alarm in VECTRABANK_MONITORING['alarms']:
        thresh_str = f"Alarm: > {alarm['threshold']}"
        print(f"  {alarm['name']:<30s} {thresh_str:<35s}")

    # ── Cost Estimation ──
    if VECTRABANK_AGENTS:
        print(f"\n{'━' * 70}")
        print("  4. Monthly Cost Estimation (10,000 requests/day)")
        print(f"{'━' * 70}")
        costs = estimate_monthly_costs(VECTRABANK_AGENTS)
        print(f"\n  {'Component':<25s} {'Model':<40s} {'Monthly':>10s}")
        print(f"  {'─' * 75}")
        for name, data in costs.items():
            if name == "TOTAL":
                print(f"  {'─' * 75}")
            model = data.get("model", "—")
            cost = data["monthly_cost"]
            print(f"  {name:<25s} {model:<40s} ${cost:>9.2f}")

    # ── Operational Runbook ──
    print(f"\n{'━' * 70}")
    print("  5. Operational Runbook")
    print(f"{'━' * 70}")
    for key, runbook in OPERATIONAL_RUNBOOK.items():
        print(f"\n  Procedure: {runbook['name']} (Est. {runbook['estimated_duration_minutes']} mins)")
        if "rollback_trigger" in runbook:
            print(f"  Rollback Trigger: {runbook['rollback_trigger']}")
        if "threshold" in runbook:
            print(f"  Trigger Threshold: {runbook['threshold']}")
        if "trigger_threshold" in runbook:
            print(f"  Trigger Threshold: {runbook['trigger_threshold']}")
        print(f"  Steps:")
        for step in runbook['steps']:
            print(f"    - {step}")

    print(f"\n{'━' * 70}")
    print(f"  Key Takeaways:")
    print(f"  1. VPC NETWORK MODE — financial services agents stay internal")
    print(f"  2. MULTI-MODEL COST OPTIMIZATION — Lite for routing/retrieval, Sonnet for synthesis")
    print(f"  3. STRICTER THRESHOLDS — 2% error rate for financial compliance")
    print(f"  4. OPERATIONAL RUNBOOK — deploy, rollback, kill switch, latency procedures (NEW)")
    print(f"  5. AUDIT TRAIL — X-Ray at 10% sampling + full guardrail audit log\n")


if __name__ == "__main__":
    main()
