FROM postgres:9.6-alpine

RUN apk update \
    && apk add --update --no-cache python3 python3-dev musl build-base libressl-dev libffi-dev ca-certificates \
    && pip3 install azure-storage-file \
    && apk del --purge build-base python3-dev libressl-dev libffi-dev \
    && rm /var/cache/apk/*

COPY run.py /usr/local/bin/
CMD ["run.py"]