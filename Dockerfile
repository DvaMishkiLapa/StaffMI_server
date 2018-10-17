FROM alpine

COPY exec.sh /exec.sh

RUN \
    chmod +x /exec.sh && \
    apk add --update --no-cache python3 && \
    pip3 install --upgrade pip && \
    pip3 install Flask gunicorn pymongo PyJWT jsonschema && \
    rm -rf /var/cache/apk/*

CMD ["/exec.sh"]
