import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_message(message: str, level: str = "info"):
    if not SLACK_WEBHOOK_URL:
        print("No Slack webhook configured")
        return

    emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "critical": "🚨",
        "killed": "💀"
    }.get(level, "ℹ️")

    payload = {
        "text": f"{emoji} *AI Sentinel Alert*\n{message}\n_Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_"
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print(f"Slack alert sent: {level}")
        else:
            print(f"Slack error: {response.status_code}")
    except Exception as e:
        print(f"Slack error: {e}")


def alert_budget_warning(spend: float, budget: float, percent: float):
    send_slack_message(
        f"Budget at *{percent:.1f}%*\nSpent: `${spend:.6f}` of `${budget:.2f}` limit\nMonitor closely — approaching limit.",
        level="warning"
    )


def alert_kill_switch(spend: float, budget: float):
    send_slack_message(
        f"*KILL SWITCH ACTIVATED* 💀\nSpent: `${spend:.6f}` — Budget limit `${budget:.2f}` reached!\nAll AI API calls are now BLOCKED.",
        level="killed"
    )


def alert_anomaly(message: str):
    send_slack_message(message, level="critical")


def alert_info(message: str):
    send_slack_message(message, level="info")


if __name__ == "__main__":
    # Test the alerts
    alert_info("AI Sentinel is online and monitoring your AI infrastructure.")
    print("Test alert sent — check your Slack!")