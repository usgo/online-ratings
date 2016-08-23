#!/usr/bin/env bash

# Simple script to Build a docker image and push to the USGO Org's Docker hub
# repository.
if [ "$TRAVIS_BRANCH" == "release" ]; then
  # Take the first 7 digits of the hash.
  WEB_IMAGE=usgo/online-ratings-web:${TRAVIS_COMMIT:0:7}
  WEB_IMAGE_LATEST=usgo/online-ratings-web:latest

  echo "Building and pushing image: $WEB_IMAGE + (update the latest version)"

  docker build -t $WEB_IMAGE web/
  docker build -t $WEB_IMAGE_LATEST web/

  docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"

  docker push $WEB_IMAGE
  docker push $WEB_IMAGE_LATEST
fi
