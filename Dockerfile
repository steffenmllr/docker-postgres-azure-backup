FROM postgres:9.6-alpine

RUN apk update \
    && apk add --update --no-cache python3 python3-dev musl build-base python3 python3-dev libressl-dev libffi-dev ca-certificates \
    && pip3 install azure-storage-file

COPY run.py /usr/local/bin/
CMD ["run.py"]