#!groovy

def warn(String message) {
    slackSend message: "${env.JOB_NAME}: ${message}: ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'
}

properties([[$class: 'ThrottleJobProperty'],
pipelineTriggers([cron('* * * * *')])])

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
        sh "docker-compose run --rm tests ./pyresttest.sh https://api-acc.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "REST Tests against ACC failed"
        currentBuild.result = 'UNSTABLE'
    }

    try {
        sh "docker-compose run --rm tests ./robs_tests.py https://api-acc.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "Robs Tests against ACC failed"
        currentBuild.result = 'UNSTABLE'
    }


    stage "Test against Production"
    try {
        sh "docker-compose run --rm tests ./pyresttest.sh https://api.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "REST Tests against PROD failed"
        currentBuild.result = 'UNSTABLE'
    }

    try {
        sh "docker-compose run --rm tests ./robs_tests.py https://api.datapunt.amsterdam.nl"
    }
    catch (Throwable t) {
        warn "Robs Tests against PROD failed"
        currentBuild.result = 'UNSTABLE'
    }



}