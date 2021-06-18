FROM python:3.8-buster

EXPOSE 8080

ENV PORT 8080

COPY . /hibi

WORKDIR /hibi

RUN mkdir ./configs && \
    touch configs/.env && \
    pip install . --prefer-binary

CMD cd /hibi && \
    python -m hibiapi --port $PORT