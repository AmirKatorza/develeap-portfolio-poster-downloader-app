def findLatestTag(tags, releaseVersion) {
    def tagArray = tags.split('\n')
    def latestTag = null

    // Iterate through the tags to find a tag starting with releaseVersion
    for (tag in tagArray) {
        if (tag.startsWith(releaseVersion)) {
            latestTag = tag
            break
        }
    }

    return latestTag // returns latestTag variable
}

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
        APP_PORT = '5001'
        APP_NAME = 'poster-downloader'
        
        // AWS configuration
        AWS_DEFAULT_REGION = 'us-east-1'
        ECR_URI = '644435390668.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPO = 'amirk-poster-downloader'
        
        // DEPLOY_PORT = '80' 
    }    

    stages {
        stage("Checkout SCM") {
            steps {
                echoStageName()
                deleteDir()
                checkout scm
            }

        stage('Version calculation') {
            steps {
                echoStageName()
                script {
                    sshagent(credentials: ["${REPO_CRED_ID}"]) {
                        def releaseVersion = sh(script: 'cat version.txt', returnStdout: true).trim()

                        // Get all tags
                        sh 'git fetch --tags'
                        def tags = sh(script: 'git tag -l --merge | sort -r -V', returnStdout: true).trim()

                        def latestTag = findLatestTag(tags, releaseVersion)
                        def calculatedVersion = ''

                        if (latestTag) {
                            /* groovylint-disable-next-line UnusedVariable */
                            def (major, minor, patch) = latestTag.tokenize('.')
                            patch = patch.toInteger() + 1
                            calculatedVersion = "${releaseVersion}.${patch}"
                        } else {
                            calculatedVersion = "${releaseVersion}.0"
                        }

                        env.LATEST_TAG = latestTag
                        env.RELEASE_VERSION = releaseVersion
                        env.CALCULATED_VERSION = calculatedVersion
                    }
                }
            }
        }
        }