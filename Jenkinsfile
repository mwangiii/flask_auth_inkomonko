pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "flask_auth_inkomonko"
    PROMETHEUS_HOST = "http://51.21.128.35:9090"
  }

  stages {

    stage('Set Compose Command') {
      steps {
        script {
          echo "Using: docker-compose"
          env.DOCKER_COMPOSE_CMD = "echo docker-compose"
        }
      }
    }

    stage('Initial Cleanup') {
      steps {
        echo "Cleaning up previous Docker containers..."
        sh 'echo "[SKIPPED] docker-compose down --remove-orphans"'
        sh 'echo "[SKIPPED] docker system prune -f -a --volumes"'
      }
    }

    stage('Clone') {
      steps {
        echo "Cloning repository..."
        sh 'echo "[SKIPPED] git clone ..."'
      }
    }

    stage('Prepare .env File') {
      steps {
        echo "Renaming 'environments' to '.env'..."
        sh 'echo "[SKIPPED] mv environments .env"'
      }
    }

    stage('Tests (Skipped)') {
      steps {
        echo "Skipping tests for now..."
        sh 'echo "[SKIPPED] test execution"'
      }
    }

    stage('Build and Start with Docker Compose') {
      steps {
        echo "Building and starting containers with Docker Compose..."
        sh 'echo "[SKIPPED] docker-compose up -d --build"'
      }
    }

    stage('Prometheus Health Check') {
      steps {
        echo "Querying Prometheus for application health..."
        sh 'echo "[SKIPPED] curl to Prometheus and check status"'
      }
    }

  }

  post {
    always {
      echo "Pipeline finished."
    }
  }
}
