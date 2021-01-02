FROM python:3.8-buster
COPY . /hibi
WORKDIR /hibi
RUN pip install -r requirements.txt --prefer-binary && \
    touch configs/.env
EXPOSE 8080
ENV GENERAL_SERVER_PORT=$PORT
CMD poetry run python main.py