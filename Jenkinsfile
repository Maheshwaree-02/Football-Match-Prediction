pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t maheshapp .'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 8081:80 maheshapp'
            }
        }

    }
}
