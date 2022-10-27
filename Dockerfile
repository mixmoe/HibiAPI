FROM python:bullseye

EXPOSE 8080

ENV PORT=8080 \
    PROCS=1 \
    GENERAL_SERVER_HOST=0.0.0.0

COPY . /hibi

WORKDIR /hibi

RUN pip install .

CMD hibiapi run --port $PORT --workers $PROCS

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD httpx --verbose --follow-redirects http://127.0.0.1:${PORT}