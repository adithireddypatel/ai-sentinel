FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir openai fastapi uvicorn boto3 pydantic requests python-dotenv

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.proxy:app", "--host", "0.0.0.0", "--port", "8000"]