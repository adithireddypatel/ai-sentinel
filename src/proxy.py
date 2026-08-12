cat > src/proxy.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import boto3
from src.alerting import alert_budget_warning, alert_kill_switch
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Sentinel Proxy")

# Lazy initialization
client = None
cloudwatch = None

def get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
        client = OpenAI(api_key=api_key)
    return client

def get_cloudwatch():
    global cloudwatch
    if cloudwatch is None:
        cloudwatch = boto3.client("cloudwatch", region_name=os.getenv("AWS_REGION", "ap-south-1"))
    return cloudwatch

INPUT_COST_PER_TOKEN  = 0.00000015
OUTPUT_COST_PER_TOKEN = 0.0000006

MONTHLY_BUDGET  = float(os.getenv("MONTHLY_BUDGET_USD", 5.0))
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD_PERCENT", 80)) / 100
KILL_THRESHOLD  = float(os.getenv("KILL_THRESHOLD_PERCENT", 100)) / 100

session_spend = {"total_usd": 0.0, "call_count": 0, "killed": False}

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    model: str = "gpt-4o-mini"

class ChatResponse(BaseModel):
    response: str
    cost_usd: float
    total_session_spend: float
    latency_ms: int
    status: str

def send_to_cloudwatch(metric_name: str, value: float, unit: str = "None"):
    try:
        get_cloudwatch().put_metric_data(
            Namespace="AISentinel",
            MetricData=[{
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit,
                "Timestamp": datetime.utcnow(),
                "Dimensions": [{"Name": "Environment", "Value": "production"}]
            }]
        )
    except Exception as e:
        print(f"CloudWatch error: {e}")

def check_budget(cost: float) -> str:
    session_spend["total_usd"] += cost
    spend = session_spend["total_usd"]
    budget = MONTHLY_BUDGET
    percent = (spend / budget) * 100
    if spend >= budget * KILL_THRESHOLD:
        session_spend["killed"] = True
        send_to_cloudwatch("KillSwitchActivated", 1)
        alert_kill_switch(spend, budget)
        return "KILLED"
    elif spend >= budget * ALERT_THRESHOLD:
        send_to_cloudwatch("BudgetAlert", 1)
        alert_budget_warning(spend, budget, percent)
        return "WARNING"
    return "OK"

@app.get("/health")
def health():
    return {
        "status": "running",
        "total_spend": round(session_spend["total_usd"], 6),
        "call_count": session_spend["call_count"],
        "killed": session_spend["killed"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if session_spend["killed"]:
        raise HTTPException(
            status_code=429,
            detail="AI Sentinel kill switch activated — budget limit reached. All AI calls blocked."
        )
    start = time.time()
    try:
        response = get_client().chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": request.message}]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    latency_ms = round((time.time() - start) * 1000)
    input_tokens  = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    cost = (input_tokens * INPUT_COST_PER_TOKEN) + (output_tokens * OUTPUT_COST_PER_TOKEN)
    session_spend["call_count"] += 1
    status = check_budget(cost)
    send_to_cloudwatch("CallCost", cost)
    send_to_cloudwatch("Latency", latency_ms, "Milliseconds")
    send_to_cloudwatch("TotalSpend", session_spend["total_usd"])
    send_to_cloudwatch("CallCount", 1, "Count")
    log = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": request.user_id,
        "model": request.model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": round(cost, 6),
        "total_spend": round(session_spend["total_usd"], 6),
        "latency_ms": latency_ms,
        "status": status
    }
    print(json.dumps(log))
    return ChatResponse(
        response=response.choices[0].message.content,
        cost_usd=round(cost, 6),
        total_session_spend=round(session_spend["total_usd"], 6),
        latency_ms=latency_ms,
        status=status
    )
EOF