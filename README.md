# AI Sentinel 🛡️

An autonomous AI safety net that monitors, controls, and protects your AI infrastructure in real time.

## The Problem
Companies are waking up to massive unexpected AI bills because of runaway API loops, abuse, or misconfigured retries. Nobody was watching. AI Sentinel watches for you — 24/7, autonomously.

## How It Works
Every AI API call goes through AI Sentinel first:
1. **Intercepts** every OpenAI API call via a FastAPI proxy
2. **Tracks** cost, latency, and usage in real time
3. **Sends metrics** to AWS CloudWatch automatically
4. **Alerts** via Slack when spending approaches the budget limit
5. **Activates kill switch** autonomously when budget is exceeded — blocking all further AI calls
6. **Visualizes** everything on a live Grafana dashboard

## Tech Stack
- **Python + FastAPI** — proxy API
- **OpenAI API** — the AI being protected
- **AWS CloudWatch** — real-time metrics and alarms
- **AWS S3** — incident log storage
- **Grafana** — live observability dashboard
- **Terraform** — AWS infrastructure as code
- **Docker** — containerized deployment
- **GitHub Actions** — CI/CD pipeline
- **Slack** — real-time alerts

## Architecture
User Request → AI Sentinel Proxy → OpenAI API
↓
Cost + Latency Tracking
↓
AWS CloudWatch Metrics
↓
Grafana Dashboard (live visualization)
↓
Budget Check → Slack Alert / Kill Switch

## Quick Start
```bash
git clone https://github.com/adithireddypatel/ai-sentinel
cd ai-sentinel
pip install -r requirements.txt
cp .env.example .env  # add your keys
uvicorn src.proxy:app --reload --port 8000
```

## Run with Docker
```bash
docker build -t ai-sentinel .
docker run -p 8000:8000 --env-file .env ai-sentinel
```

## Infrastructure Setup
```bash
cd terraform
terraform init
terraform apply
```

## API Endpoints
- `GET /health` — system status, spend, call count
- `POST /chat` — send a message through the sentinel proxy

## Demo
🎥 https://youtu.be/4Jy2agrx86g

## GitHub
github.com/adithireddypatel/ai-sentinel
