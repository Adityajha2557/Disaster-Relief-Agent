
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'adityajha2557/drraa'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checked out from GitHub'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %DOCKER_IMAGE%:%BUILD_NUMBER% -t %DOCKER_IMAGE%:latest .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    bat '''
                        @echo off
                        echo %DOCKER_TOKEN% | docker login -u %DOCKER_USER% --password-stdin
                        docker push %DOCKER_IMAGE%:%BUILD_NUMBER%
                        docker push %DOCKER_IMAGE%:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'DRRAA Docker image built and pushed successfully!'
        }
        failure {
            echo 'DRRAA pipeline failed. Check the console output.'
        }
    }
}
