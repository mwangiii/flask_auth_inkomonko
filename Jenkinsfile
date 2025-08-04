pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "flask_auth_inkomonko"
    PROMETHEUS_HOST = "http://51.21.128.35:9090" // Change this if needed
  }

  stages {

    stage('Initial Cleanup') {
      when {
        branch 'main'
      }
      steps {
        echo "Cleaning up previous Docker containers..."
        sh '''
          docker compose down --remove-orphans || true
          docker system prune -f -a --volumes || true
        '''
      }
    }

    stage('Clone Repository') {
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
            echo "ERROR: 'environments' file not found!"
            exit 1
          fi
        '''
      }
    }

    stage('Run Tests (Placeholder)') {
      steps {
        echo "Skipping tests for now..."
        sh 'echo "Tests would go here."'
      }
    }

    stage('Build and Deploy with Docker Compose') {
      when {
        branch 'main'
      }
      steps {
        echo "Building and starting containers with Docker Compose..."
        sh '''
          docker compose build
          docker compose up -d
        '''
      }
    }

    stage('Prometheus Health Check') {
      when {
        branch 'main'
      }
      steps {
        echo "Checking Prometheus metrics endpoint..."
        sh '''
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
      echo "Pipeline execution completed."
    }
  }
}
