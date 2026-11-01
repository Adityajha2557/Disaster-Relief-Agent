
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'adityajha2557/drraa'
        EC2_HOST = '65.0.93.54'
    }

    stages {
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

        stage('Deploy to AWS EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=accept-new ubuntu@%EC2_HOST% "sudo docker pull adityajha2557/drraa:latest && (sudo docker rm -f drraa-container || true) && sudo docker run -d --name drraa-container --restart unless-stopped --env-file /home/ubuntu/Disaster-Relief-Agent/.env -p 127.0.0.1:8501:8501 -v /home/ubuntu/Disaster-Relief-Agent/database:/app/database adityajha2557/drraa:latest"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'DRRAA build, push and EC2 deployment completed!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
