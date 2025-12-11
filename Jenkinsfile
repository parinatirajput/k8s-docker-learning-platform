pipeline {
    agent any

    environment {
        AWS_REGION = "us-east-1"
        ECR_REGISTRY = "850601428312.dkr.ecr.us-east-1.amazonaws.com"
        ECR_REPO = "flask-runner"
        IMAGE_TAG = "latest"
    }

    stages {

        stage("Clone Repo") {
            steps {
                git branch: 'main',
                    url: 'https://github.com/parinatirajput/k8s-docker-learning-platform.git',
                    credentialsId: 'github-pat'
            }  
      }

        stage("Build Docker Image") {
            steps {
                sh """
                docker build -t $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG .
                """
            }
        }

        stage("Push to ECR") {
            steps {
                withAWS(credentials:'aws-creds', region: "${AWS_REGION}") {

                    // Login to ECR
                    sh """
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}
                    """

                    // Push the image
                    sh """
                    docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    """
                }
            }
        }

        stage("Deploy with CloudFormation") {
            steps {
                withAWS(credentials:'aws-creds', region:"${AWS_REGION}") {
                    sh """
                    aws cloudformation deploy \
                        --template-file cloudformation-app.yaml \
                        --stack-name flask-app-stack \
                        --capabilities CAPABILITY_NAMED_IAM \
                        --parameter-overrides \
                            KeyName=practice \
                            DockerImage=${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    """
                }
            }
        }
    }
}

