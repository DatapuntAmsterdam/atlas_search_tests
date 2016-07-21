#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}

def warn(String message) {
    slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'
}


node {
    stage "Checkout"
    checkout scm

    stage "Build"
    try {
        sh "docker-compose build"
    }
    catch (Throwable t) {
        warn "Could not build docker images"
        throw t
    }

    stage "Test against Acceptance"
    try {
        sh "docker-compose run tests ./pyresttest.sh https://api-acc.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "REST Tests against ACC failed"
        currentBuild.result = 'FAILURE'
    }

    try {
        sh "docker-compose run tests ./robs_tests.sh https://api-acc.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "Robs Tests against ACC failed"
        currentBuild.result = 'FAILURE'
    }


    stage "Test against Production"
    try {
        sh "docker-compose run tests ./pyresttest.sh https://api.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "REST Tests against PROD failed"
        currentBuild.result = 'FAILURE'
    }

    try {
        sh "docker-compose run tests ./robs_tests.sh https://api.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "Robs Tests against PROD failed"
        currentBuild.result = 'FAILURE'
    }



}