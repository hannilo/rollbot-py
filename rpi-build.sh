#!/bin/sh
docker build --no-cache -t rollbot . && \
docker run --name=rollbot --restart=always -d rollbot
