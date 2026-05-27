# SmartCart AI – DiscountMate

SmartCart AI – DiscountMate is an interactive grocery savings web application created for SIT753 Task 7.3HD: DevOps Pipeline with Jenkins.

## Project Background

This project is based on the 7.2D topic: SmartCart AI for DataBytes – DiscountMate.

The application helps users:
- Compare grocery prices
- Predict discounts
- Find cheaper substitutes
- Generate simple budget meal baskets
- View health and monitoring metrics

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Docker
- Docker Compose
- Jenkins
- Pytest
- Flake8
- Pylint
- Bandit
- Prometheus metrics

## Application Features

1. Interactive grocery dashboard
2. Price comparison
3. Discount prediction
4. Smart substitute recommendation
5. Budget meal planner
6. Health check endpoint
7. Prometheus metrics endpoint

## API Endpoints

| Endpoint | Description |
|---|---|
| `/` | Interactive dashboard |
| `/health` | Application health check |
| `/api/products` | Product dataset |
| `/compare?item=milk` | Compare prices |
| `/predict-discount?item=bread` | Predict discount recommendation |
| `/substitute?item=rice` | Recommend cheaper substitute |
| `/meal-plan?budget=20` | Generate budget meal basket |
| `/metrics` | Prometheus metrics |

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
python app.py
```

Open:

```text
http://localhost:5000
```

## Run Tests

```bash
pytest tests/ --cov=app
```

## Run Code Quality Checks

```bash
flake8 app.py tests/ --max-line-length=100
pylint app.py --fail-under=8.0
```

## Run Security Scan

```bash
bandit -r . -x .venv,tests -ll
```

## Build Docker Image

```bash
docker build -t smartcart-ai:local .
```

## Run Docker Container

```bash
docker run -p 5000:5000 smartcart-ai:local
```

Open:

```text
http://localhost:5000
```

## Jenkins Pipeline Stages

The Jenkins pipeline includes all 7 required HD stages:

1. Build
2. Test
3. Code Quality
4. Security
5. Deploy to Staging
6. Release to Production
7. Monitoring and Alerting

## Staging URL

```text
http://localhost:5001
```

## Production URL

```text
http://localhost:5002
```

## Monitoring

The app exposes Prometheus-compatible metrics at:

```text
/metrics
```