pipeline {
    agent any

    triggers {
        pollSCM('H/15 * * * *')
    }

    options {
        timestamps()
        timeout(time: 10, unit: 'MINUTES')
    }

    environment {
        APP_PORT = '80'
        APP_NAME = 'poster-downloader'
        AWS_DEFAULT_REGION = 'us-east-1'
        ECR_URI = '644435390668.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPO = 'amirk-poster-downloader'
        NGINX_SERVICE = 'reverse-proxy-nginx'
        SSH_CRED_ID = 'github-ssh-key'
        GITOPS_REPO_NAME = 'develeap-portfolio-poster-downloader-gitops'
        GITOPS_REPO_URL = 'git@github.com:AmirKatorza/develeap-portfolio-poster-downloader-gitops.git'
        GIT_USER_NAME = 'Jenkins'
        GIT_USER_EMAIL = 'amir.katorza@gmail.com'
    }    

    stages {
        stage("Checkout SCM") {
            steps {
                echoStageName()
                deleteDir()
                checkout scm
            }
        }

        stage('Version calculation') {
            steps {
                echoStageName()
                script {
                    sshagent(credentials: ["${SSH_CRED_ID}"]) {
                        
                        // Fetch all tags
                        sh 'git fetch --tags'
                        def tags = sh(script: 'git tag -l --sort=-v:refname', returnStdout: true).trim()

                        // Find the latest tag
                        def latestTag = tags.tokenize('\n')[0] ?: '0.0.0'

                        // Determine version increment type based on last commit message
                        def incrementType = determineVersionIncrement()
                        def calculatedVersion = calculateNextVersion(latestTag, incrementType)
                        echo "Calculated version: ${calculatedVersion}"

                        // Set environment variables
                        env.LATEST_TAG = latestTag ?: 'N/A'                        
                        env.CALCULATED_VERSION = calculatedVersion                        
                    }
                }
            }
        }        

        stage("Build Docker Image") {
            steps {
                echoStageName()
                sh "docker build -t ${APP_NAME}:${CALCULATED_VERSION} ."                
            }
        }

        stage("Run App With Nginx") {
            steps {
                echoStageName()                
                sh "docker compose down -v || true"
                sh "docker compose up -d"
                sh "sleep 10"
            }
        }

        stage('Debug Services & Networks') {
            steps {
                echoStageName()
                script {
                    // List all running containers
                    echo "Listing all running containers..."
                    sh 'docker ps'

                    // Optionally, list all networks to see all connected containers
                    echo "Listing all networks..."
                    sh 'docker network ls'

                    // Inspecting ci_network to see which containers are connected
                    echo "Inspecting ci_network..."
                    sh 'docker network inspect ci_network'
                }
            }
        }

        stage("Nginx Health Check") {            
            steps {
                echoStageName()
                sh '''
                    CURL_EXIT_CODE=0
                    curl -fsSLi http://${NGINX_SERVICE}:${APP_PORT} --max-time 20 || CURL_EXIT_CODE="$?"
                    echo "cURL Exit Code: ${CURL_EXIT_CODE}"
                    if [ $CURL_EXIT_CODE -ne 0 ]; then
                        echo "App is NOT running correctly!"
                        docker compose down -v || true
                        exit 1
                    else
                        echo "App is running correctly!"
                        docker compose down -v || true
                    fi
                ''' 
            }
        }

        stage("Tag Image") {
            steps {
                echoStageName()
                script {
                    // Tag the Docker image for ECR
                    sh '''
                        echo "Tagging Docker images for ECR..."
                        docker tag ${APP_NAME}:${CALCULATED_VERSION} ${ECR_URI}/${ECR_REPO}:${CALCULATED_VERSION}                        
                    '''
                }
            }
        }

        stage("Push to ECR") {
            steps {
                echoStageName()
                script {
                    // Authenticate Docker with ECR
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials',
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        sh '''
                            echo "Authenticating Docker with ECR..."
                            aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $ECR_URI
                            
                            echo "Pushing Docker image to ECR..."
                            docker push ${ECR_URI}/${ECR_REPO}:${CALCULATED_VERSION}                            
                        '''
                    }                    
                }
            }
        }

        stage('Git Tag & Clean') {
            steps {
                echoStageName()
                sshagent(credentials: ["${SSH_CRED_ID}"]) {
                    sh """
                        git clean -f
                        git reset --hard
                        git tag ${CALCULATED_VERSION}
                        git push origin ${CALCULATED_VERSION}
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                echoStageName()
                cleanWs()
                sshagent(credentials: ["${SSH_CRED_ID}"]) {
                    sh "git clone ${GITOPS_REPO_URL} ${GITOPS_REPO_NAME}"
                    dir(GITOPS_REPO_NAME) {
                        sh """
                            git checkout main
                            git config user.name '${GIT_USER_NAME}'
                            git config user.email '${GIT_USER_EMAIL}'
                        """
                    }
                }                

                dir("${GITOPS_REPO_NAME}/cluster-resources/poster-downloader-chart") {
                    // Using yq to replace the image tag in values.yaml
                    sh """
                        yq eval '.app.image.tag = "${CALCULATED_VERSION}"' -i values.yaml
                    """
                }

                sshagent(credentials: ["${SSH_CRED_ID}"]) {
                    dir(GITOPS_REPO_NAME) {
                        sh """
                            git add .
                            git commit -m 'Jenkins Deploy - Build No. ${BUILD_NUMBER}, Version ${CALCULATED_VERSION}'
                            git push origin main
                        """
                    }
                }
            }
        }
    }   

    post {
        always {
            sh '''
                docker image rm ${ECR_URI}/${ECR_REPO}:${CALCULATED_VERSION} || true
                docker image prune -af
                docker volume prune -af
                docker container prune -f
                docker network prune -f                
            '''
            cleanWs()
        }
    }
}       

// Custom function to echo the current stage name (optional for clarity in logs)
def echoStageName() {
    echo "================== ${env.STAGE_NAME} Stage =================="
}

// Determine version increment type based on last commit message
def determineVersionIncrement() {
    def lastCommitMsg = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim().toLowerCase()

    if (lastCommitMsg.contains('major')) {
        return 'MAJOR'
    } else if (lastCommitMsg.contains('minor')) {
        return 'MINOR'
    } else {
        return 'PATCH'
    }
}

// Calculate the next version based on the latest tag and increment type
def calculateNextVersion(String latestTag, String incrementType) {
    def (major, minor, patch) = latestTag.tokenize('.').collect { it.toInteger() }
    
    switch (incrementType) {
        case 'MAJOR':
            major += 1
            minor = 0
            patch = 0
            break
        case 'MINOR':
            minor += 1
            patch = 0
            break
        case 'PATCH':
            patch += 1
            break
    }
    
    return "${major}.${minor}.${patch}"
}