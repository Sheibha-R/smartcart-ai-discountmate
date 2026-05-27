pipeline {
    agent any

    environment {
        APP_NAME = "smartcart-ai"
        IMAGE_NAME = "smartcart-ai"
        STAGING_PORT = "5001"
        PROD_PORT = "5002"
    }

    options {
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out SmartCart AI - DiscountMate source code...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image and creating build artefact...'

                sh '''
                    docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                    docker save ${IMAGE_NAME}:${BUILD_NUMBER} -o smartcart-ai-${BUILD_NUMBER}.tar
                '''

                archiveArtifacts artifacts: "smartcart-ai-${BUILD_NUMBER}.tar", fingerprint: true
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated unit tests with Pytest...'

                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                    pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml
                '''
            }

            post {
                always {
                    junit 'test-results.xml'
                    archiveArtifacts artifacts: 'coverage.xml', fingerprint: true
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Running code quality checks using Flake8 and Pylint...'

                sh '''
                    . .venv/bin/activate
                    flake8 app.py tests/ --max-line-length=100
                    pylint app.py --fail-under=8.0

                    if command -v sonar-scanner >/dev/null 2>&1; then
                        sonar-scanner
                    else
                        echo "SonarQube scanner not installed. Continuing with Flake8 and Pylint checks."
                    fi
                '''
            }
        }

        stage('Security') {
            steps {
                echo 'Running automated security scan using Bandit...'

                sh '''
                    . .venv/bin/activate
                    bandit -r . -x .venv,tests -ll -f json -o bandit-report.json
                    bandit -r . -x .venv,tests -ll
                '''

                archiveArtifacts artifacts: 'bandit-report.json', fingerprint: true
            }
        }

        stage('Deploy to Staging') {
            steps {
                echo 'Deploying SmartCart AI to staging Docker environment...'

                sh '''
                    export BUILD_NUMBER=${BUILD_NUMBER}

                    docker compose -f docker-compose.staging.yml down || true
                    docker compose -f docker-compose.staging.yml up -d

                    echo "Waiting for staging application to start..."
                    sleep 10

                    curl -f http://localhost:${STAGING_PORT}/health
                '''
            }
        }

        stage('Release to Production') {
            steps {
                echo 'Promoting validated build to production...'

                sh '''
                    docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest

                    docker compose -f docker-compose.prod.yml down || true
                    docker compose -f docker-compose.prod.yml up -d

                    echo "Waiting for production application to start..."
                    sleep 10

                    curl -f http://localhost:${PROD_PORT}/health
                '''
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo 'Checking production health and Prometheus metrics...'

                sh '''
                    curl -f http://localhost:${PROD_PORT}/health -o production-health.json
                    curl -f http://localhost:${PROD_PORT}/metrics -o production-metrics.txt

                    grep smartcart_requests_total production-metrics.txt

                    echo "Monitoring check passed. Production metrics are available."
                '''

                archiveArtifacts artifacts: 'production-health.json,production-metrics.txt', fingerprint: true
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: All 7 HD pipeline stages completed successfully.'
        }

        failure {
            echo 'FAILED: One or more stages failed. Check Jenkins console output.'
        }

        always {
            echo 'Cleaning temporary Python environment...'
            sh 'rm -rf .venv || true'
        }
    }
}