# Step-by-Step Rebuild Guide

This guide breaks the project into small stages so you can rebuild it slowly and understand each part.

## Stage 1: Train a Model

Goal:
- learn how HDFS logs become an anomaly classifier

Files to focus on:
- `src/data/hdfs.py`
- `src/models/train.py`

What happens:
- create or load HDFS log data
- vectorize the log message text and encode metadata
- train a scikit-learn model
- save the model to `artifacts/model.joblib`

Run:

```bash
.venv\Scripts\python -m src.models.train
```

## Stage 2: Serve the Model with an API

Goal:
- send an HDFS log record to an endpoint and get an anomaly prediction

Files to focus on:
- `app/main.py`

What happens:
- load the saved model
- expose `/health`
- expose `/predict`
- expose `/metrics`

Run:

```bash
.venv\Scripts\python -m uvicorn app.main:app --reload
```

## Stage 3: Test the Project

Goal:
- verify training and API behavior automatically

Files to focus on:
- `tests/test_training.py`
- `tests/test_api.py`

Run:

```bash
.venv\Scripts\python -m pytest
```

## Stage 4: Containerize It

Goal:
- run the app inside Docker

Files to focus on:
- `Dockerfile`
- `docker-compose.yml`

## Stage 5: Add CI/CD

Goal:
- run tests and build the Docker image automatically on push

Files to focus on:
- `.github/workflows/ci.yml`

## Stage 6: Deploy to Kubernetes

Goal:
- move from local development to cluster deployment

Files to focus on:
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/prometheus-monitor.yaml`

## Suggested Learning Order

1. Run the training script.
2. Open the saved metrics and model artifacts.
3. Run the API locally.
4. Send one prediction request.
5. Run the tests.
6. Build the Docker image.
7. Look at CI/CD.
8. Look at Kubernetes.
