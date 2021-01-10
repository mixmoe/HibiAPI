FROM python:3.8-alpine
COPY . /hibi
WORKDIR /hibi
RUN pip install poetry && \
    poetry install --no-dev && \
    touch configs/.env
EXPOSE 8080
ENV GENERAL_SERVER_PORT=$PORT
CMD poetry run python main.py