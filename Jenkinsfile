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
        REPO_CRED_ID = ''
    }    

    stages {
        stage("Checkout SCM") {
            steps {
                echo "Checkout SCM Stage"
                deleteDir()
                checkout scm
            }
        }

        stage('Version calculation') {
            steps {
                echo "Version calculation Stage"
                script {
                    sshagent(credentials: ["${REPO_CRED_ID}"]) {
                        // Read base release version
                        def releaseVersion = sh(script: 'cat version.txt', returnStdout: true).trim()

                        // Fetch all tags
                        sh 'git fetch --tags'
                        def tags = sh(script: 'git tag -l --sort=-v:refname', returnStdout: true).trim()

                        // Determine version increment type based on last commit message
                        def incrementType = determineVersionIncrement()
                        def latestTag = tags.tokenize('\n').find { it.startsWith(releaseVersion) }
                        def calculatedVersion = calculateNextVersion(latestTag, incrementType)

                        // Set environment variables
                        env.LATEST_TAG = latestTag ?: 'N/A'
                        env.RELEASE_VERSION = releaseVersion
                        env.CALCULATED_VERSION = calculatedVersion
                    }
                }
            }
        }

        // Additional stages like Build, Test, and Deploy can be added here.
    }
    
    post {
        always {
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
