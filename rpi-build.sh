#!/bin/sh
docker build --no-cache -t rollbot . && \
docker run --name=rollbot --restart=on-failure:3 -d rollbot
