FROM python:3.8-buster
COPY . /hibi
WORKDIR /hibi
RUN pip install -r requirements.txt --prefer-binary && \
    touch configs/.env
CMD export GENERAL_SERVER_PORT=$PORT && \
    cd /hibi && \
    python main.py