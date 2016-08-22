#!/usr/bin/env bash

# Simple script to Build a docker image and push to the USGO Org's Docker hub
# repository.
if [ "$TRAVIS_BRANCH" == "release" ]; then
  docker build -t usgo/online-ratings-web web/
  docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
  docker push usgo/online-ratings-web
fi
