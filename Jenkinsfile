
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'GitHub repository checked out successfully'
            }
        }

        stage('Validate Project Files') {
            steps {
                sh '''
                    test -f app.py
                    test -f requirements.txt
                    test -f Dockerfile
                    test -f docker-compose.yml
                    test -d templates
                    echo "All required project files are present"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-capstone-web:latest .'
            }
        }

        stage('Deployment Preparation') {
            steps {
                echo 'Docker image build completed. Ready for Kubernetes deployment.'
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully'
        }
        failure {
            echo 'CI/CD pipeline failed. Check the console output.'
        }
    }
}
