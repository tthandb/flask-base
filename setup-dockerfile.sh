#!/bin/sh
IMAGE_TAG=$(echo $CI_COMMIT_REF_NAME | awk '{print tolower($0)}')

if [[ $IMAGE_TAG == 'master' ]]; then
  IMAGE_TAG='stable'
fi

if [[ $IMAGE_TAG == 'develop' ]]; then
  IMAGE_TAG='latest'
fi

find ./docker -type f -exec sed -i -e "s/IMAGE_NAME/$(echo $REGISTRY | sed -e 's/\//\\\//g')\/$(echo $CI_PROJECT_PATH | sed -e 's/\//\\\//g')\/base-image/g" {} \;
find ./docker -type f -exec sed -i -e "s/IMAGE_TAG/$IMAGE_TAG/g" {} \;
