FROM python:3.8-buster

EXPOSE 8080

ENV PORT=8080 PROCS=1

COPY . /hibi

WORKDIR /hibi

RUN touch .env && \
    pip install . --prefer-binary

CMD cd /hibi && \
    python -m hibiapi \
        --port $PORT --workers $PROCS