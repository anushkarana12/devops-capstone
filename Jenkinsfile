
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
                    test -f Dockerfile.test
                    test -f docker-compose.yml
                    test -d templates
                    test -d tests
                    test -f k8s/deployment.yaml
                    test -f k8s/service.yaml
                    test -f k8s/pvc.yaml
                    echo "All required project files are present"
                '''
            }
        }

        stage('Automated Unit Tests') {
            steps {
                sh '''
                    docker build -f Dockerfile.test -t devops-capstone-tests:latest .
                    docker run --rm devops-capstone-tests:latest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-capstone-web:latest .'
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config apply -f k8s/pvc.yaml
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config apply -f k8s/deployment.yaml
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config apply -f k8s/service.yaml

                    kubectl --kubeconfig=/var/jenkins_home/.kube/config rollout restart deployment/task-app
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config rollout status deployment/task-app --timeout=180s

                    kubectl --kubeconfig=/var/jenkins_home/.kube/config get deployments
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config get pods
                    kubectl --kubeconfig=/var/jenkins_home/.kube/config get services
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully. Application deployed to Kubernetes.'
        }
        failure {
            echo 'CI/CD pipeline failed. Check the console output.'
        }
    }
}
