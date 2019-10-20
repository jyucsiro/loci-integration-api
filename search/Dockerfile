FROM alpine:3.7

RUN apk add --no-cache bash
RUN apk add --no-cache jq
RUN apk add --no-cache curl
RUN apk add --no-cache coreutils

RUN mkdir -p /app
WORKDIR /app
COPY . /app


