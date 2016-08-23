#!/usr/bin/env bash

# Simple script to Build a docker image and push to the USGO Org's Docker hub
# repository.
if [ "$TRAVIS_BRANCH" == "release" ]; then
  IMAGE_TAG=$TRAVIS_COMMIT
  WEB_IMAGE=usgo/online-ratings-web:$IMAGE_TAG
  echo "Building and pushing image: $WEB_IMAGE"
  docker build -t $WEB_IMAGE web/
  docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
  docker push $WEB_IMAGE
fi
