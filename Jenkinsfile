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
          // Check if 'docker compose' works; fallback to 'docker-compose'
          def result = sh(script: 'docker compose version > /dev/null 2>&1', returnStatus: true)
          env.DOCKER_COMPOSE_CMD = (result == 0) ? 'docker compose' : 'docker-compose'
          echo "Using: ${env.DOCKER_COMPOSE_CMD}"
        }
      }
    }

    stage('Initial Cleanup') {
      when {
        branch 'main'
      }
      steps {
        echo "Cleaning up previous Docker containers..."
        sh '''
          ${DOCKER_COMPOSE_CMD} down --remove-orphans || true
          docker system prune -f -a --volumes || true
        '''
      }
    }

    stage('Clone') {
      steps {
        echo "Cloning repository..."
        checkout scm
      }
    }

    stage('Prepare .env File') {
      when {
        branch 'main'
      }
      steps {
        echo "Renaming 'environments' to '.env'..."
        sh '''
          if [ -f environments ]; then
            mv environments .env
            echo ".env file prepared."
          else
            echo "environments file not found!"
            exit 1
          fi
        '''
      }
    }

    stage('Tests (Skipped)') {
      steps {
        echo "Skipping tests for now..."
        sh 'echo "tests would run here"'
      }
    }

    stage('Build and Start with Docker Compose') {
      when {
        branch 'main'
      }
      steps {
        echo "Building and starting containers with Docker Compose..."
        sh '${DOCKER_COMPOSE_CMD} up -d --build'
      }
    }

    stage('Prometheus Health Check') {
      when {
        branch 'main'
      }
      steps {
        echo "Querying Prometheus for application health..."
        sh '''
          echo "Checking Prometheus 'up' metrics..."
          RESPONSE=$(curl -s "${PROMETHEUS_HOST}/api/v1/query?query=up")
          echo "$RESPONSE"

          echo "$RESPONSE" | grep '"value"' | grep '"1"' > /dev/null
          if [ $? -ne 0 ]; then
            echo "Prometheus did not return expected 'up' value!"
            exit 1
          else
            echo "Prometheus confirms services are UP."
          fi
        '''
      }
    }

  }

  post {
    always {
      echo "Pipeline finished."
    }
  }
}
