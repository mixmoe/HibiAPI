FROM python:3.8-buster
EXPOSE 8080
ENV PORT=8080
COPY . /hibi
WORKDIR /hibi
RUN pip install -r requirements.txt --prefer-binary && \
    touch configs/.env
CMD cd /hibi && \
    python main.py --port $PORT