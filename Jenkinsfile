
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'drraa'
        EC2_HOST = '65.0.93.54'
        EC2_USER = 'ubuntu'
        EC2_IMAGE_PATH = '/home/ubuntu/drraa-image.tar'
    }

    stages {

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t %DOCKER_IMAGE%:%BUILD_NUMBER% -t %DOCKER_IMAGE%:latest .
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Save Docker Image') {
            steps {
                bat '''
                    docker save -o drraa-image.tar %DOCKER_IMAGE%:latest
                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Transfer Image to EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    bat '''
                        scp -o StrictHostKeyChecking=accept-new drraa-image.tar %EC2_USER%@%EC2_HOST%:%EC2_IMAGE_PATH%
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                sshagent(credentials: ['ec2-ssh-key']) {
                    bat '''
                        ssh -o StrictHostKeyChecking=accept-new %EC2_USER%@%EC2_HOST% "sudo docker load -i /home/ubuntu/drraa-image.tar && (sudo docker rm -f drraa-container 2>/dev/null || true) && sudo docker run -d --name drraa-container --restart unless-stopped --env-file /home/ubuntu/Disaster-Relief-Agent/.env -p 127.0.0.1:8501:8501 -v /home/ubuntu/Disaster-Relief-Agent/database:/app/database drraa:latest && sudo rm -f /home/ubuntu/drraa-image.tar"
                        if errorlevel 1 exit /b 1
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'DRRAA successfully built and deployed directly to AWS EC2!'
        }
        failure {
            echo 'Deployment failed. Check the Console Output.'
        }
        always {
            bat 'if exist drraa-image.tar del /Q drraa-image.tar'
        }
    }
}
