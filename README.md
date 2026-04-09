# HDFS Log Anomaly Detection MLOps Project

This project is an end-to-end MLOps pipeline for detecting anomalous HDFS log events. It trains a machine learning model on Hadoop log data, serves predictions through a FastAPI API, stores prediction history in SQLite, packages the service with Docker, validates changes with GitHub Actions, and can be deployed on EC2 or Kubernetes.

## Problem Statement

Large distributed systems generate huge volumes of logs. Manually checking every log line is not realistic, so this project detects whether a new HDFS log event looks normal or anomalous.

Given a new log event, the system predicts:
- anomaly probability
- anomaly / non-anomaly label

## Why This Project Matters

This project shows more than just model training. It demonstrates how to:
- train and save an ML model
- expose the model through an API
- log predictions for later inspection
- package the application with Docker
- validate the project with CI
- deploy the application to a server
- prepare the service for Kubernetes-based deployment

## Architecture Overview

The project flow is:
1. Load HDFS log data from `data/raw/`
2. Train a text classification model
3. Save the trained model and metrics
4. Start a FastAPI inference service
5. Send log events to `/predict`
6. Return prediction results
7. Store prediction history in SQLite
8. Expose service health and Prometheus metrics

### Architecture Diagram

```mermaid
flowchart LR
    A[HDFS Log Dataset CSV] --> B[Training Pipeline]
    B --> C[Saved Model<br/>model.joblib]
    B --> D[Metrics<br/>metrics.json]
    C --> E[FastAPI Inference Service]
    E --> F[/predict]
    E --> G[/health]
    E --> H[/metrics]
    F --> I[Anomaly Prediction]
    F --> J[SQLite Prediction Log]
    K[GitHub Actions] --> L[Test + Docker Build]
    M[Docker Image] --> N[EC2 / Kubernetes Deployment]
    E --> M
```

## Tech Stack

Core ML and API:
- Python
- Pandas
- Scikit-learn
- FastAPI
- Uvicorn

MLOps / DevOps:
- Docker
- GitHub Actions
- SQLite
- Kubernetes manifests
- Prometheus metrics
- AWS EC2

## Project Structure

```text
.
|-- app/
|-- artifacts/
|-- data/
|-- docs/
|-- helm/
|-- k8s/
|-- src/
|-- tests/
|-- .github/workflows/
|-- Dockerfile
|-- docker-compose.yml
`-- requirements.txt
```

Important folders and files:
- `src/models/train.py`: training pipeline
- `src/data/hdfs.py`: fallback sample HDFS-like data
- `app/main.py`: FastAPI service
- `src/utils/prediction_store.py`: SQLite prediction logging
- `tests/`: API and training tests
- `k8s/`: Kubernetes manifests
- `.github/workflows/ci.yml`: CI workflow

## Dataset

The project is designed for an HDFS anomaly dataset with these core columns:
- `content`
- `component`
- `level`
- `block_id`
- `anomaly`

Local training can use a real CSV placed in `data/raw/`.

Example schema:

```csv
content,component,level,block_id,anomaly
"Receiving block blk_-1608999687919862906 src: /10.250.19.102:54106 dest: /10.250.19.102:50010","dfs.DataNode$DataXceiver",INFO,"blk_-1608999687919862906",0
"Received exception while serving block blk_112233445566 broken pipe","dfs.DataNode$DataXceiver",ERROR,"blk_112233445566",1
```

Note:
- large raw datasets are intentionally not committed to GitHub
- if no real CSV exists, the project falls back to a tiny built-in sample dataset so the app still runs

## Model Training

Training happens in `src/models/train.py`.

What it does:
- reads the first CSV from `data/raw/`
- falls back to sample data if no CSV exists
- vectorizes log text using TF-IDF
- encodes categorical features like component, level, and block ID
- trains a Logistic Regression classifier
- evaluates the model
- saves artifacts in `artifacts/`

Artifacts produced:
- `artifacts/model.joblib`: trained model pipeline
- `artifacts/metrics.json`: training metrics
- `artifacts/sample_payload.json`: sample request payload
- `artifacts/predictions.db`: SQLite prediction history

## API Endpoints

Base URL locally:
- `http://127.0.0.1:8000`

Endpoints:
- `GET /` : basic service message
- `GET /health` : health check and training metrics
- `POST /predict` : predict anomaly probability for a log event
- `GET /predictions/recent` : recent prediction history from SQLite
- `GET /metrics` : Prometheus-compatible metrics

Example `/predict` request:

```json
{
  "content": "Received exception while serving block blk_112233445566 broken pipe",
  "component": "dfs.DataNode$DataXceiver",
  "level": "ERROR",
  "block_id": "blk_112233445566"
}
```

Example response:

```json
{
  "anomaly_probability": 0.9927,
  "predicted_anomaly": true
}
```

## Prediction Logging

Each prediction is stored in SQLite so the system behaves more like a real ML service.

Stored fields include:
- timestamp
- content
- component
- level
- block ID
- anomaly probability
- predicted anomaly label

Example recent predictions call:

```bash
curl "http://127.0.0.1:8000/predictions/recent?limit=10"
```

## Local Development

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Train the model:

```bash
python -m src.models.train
```

Run the API:

```bash
python -m uvicorn app.main:app --reload
```

Open:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

Run tests:

```bash
python -m pytest
```

## Docker

Build the image:

```bash
docker build -t hdfs-log-anomaly-api .
```

Run the container:

```bash
docker run -p 8000:8000 hdfs-log-anomaly-api
```

Or with Compose:

```bash
docker compose up --build
```

## GitHub Actions

The CI workflow does the following on push and pull request:
- installs dependencies
- runs tests
- builds the Docker image

This validates that the repository is healthy and container-ready.

## EC2 Deployment

The Dockerized API was validated on AWS EC2.

Typical flow:
1. clone the repository on EC2
2. build the Docker image
3. run the container on port `8000`
4. open port `8000` in the EC2 security group
5. access the API from the browser

Example endpoints after deployment:
- `http://<EC2-PUBLIC-IP>:8000/health`
- `http://<EC2-PUBLIC-IP>:8000/docs`

Note:
- if the real dataset is not copied to EC2, the container uses the fallback sample dataset
- local training can still use the full real dataset

## Screenshots

### Swagger UI

![Swagger UI](docs/images/swagger-ui.png)

### Anomaly Prediction Example

![Anomaly Prediction](docs/images/anomaly-prediction.png)

### Normal Prediction Example

![Normal Prediction](docs/images/normal-prediction.png)

### Recent Prediction History

![Recent Predictions](docs/images/recent-predictions.png)

### GitHub Actions CI Success

![GitHub Actions Success](docs/images/github-actions-success.png)

### EC2 Deployment

![EC2 Deployment](docs/images/ec2-deployment.png)

## Kubernetes

Kubernetes manifests are included in `k8s/` for deployment and service exposure.

Included resources:
- deployment manifest
- service manifest
- Prometheus ServiceMonitor manifest

Recommended path:
- first validate locally with Docker or EC2
- then deploy with Minikube for a free Kubernetes setup
- later move to a managed cluster such as EKS if needed

## Current Status

This project currently supports:
- real local training on HDFS anomaly data
- FastAPI inference service
- anomaly and non-anomaly predictions
- prediction logging with SQLite
- Docker packaging
- GitHub Actions CI
- EC2 deployment
- Kubernetes manifests for the next deployment step

## Future Improvements

Planned next steps:
- deploy and validate on Minikube
- make EC2 use the full real dataset as well
- add screenshots and architecture diagram
- add experiment tracking with MLflow
- add drift monitoring
- add model version metadata endpoint
- improve preprocessing such as duplicate removal and data quality checks
