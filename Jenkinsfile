pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = "flask_auth_inkomonko"
  }

  stages {
    stage('Initial Cleanup') {
      when {
        branch 'main'
      }
      steps {
        echo "Cleaning up previous Docker containers..."
        sh '''
          docker-compose down --remove-orphans || true
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

    stage('Build and Start with Docker Compose') {
      when {
        branch 'main'
      }
      steps {
        echo "Building and starting containers with Docker Compose..."
        sh "docker-compose up -d --build"
      }
    }
  }

  post {
    always {
      echo "Pipeline finished."
    }
  }
}
