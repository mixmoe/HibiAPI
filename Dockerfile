FROM python:3.8-buster
COPY . /hibi
WORKDIR /hibi
RUN pip install -r requirements.txt --prefer-binary && \
    touch configs/.env
ENV PORT=8080
EXPOSE 8080
CMD pythoh main.py --port $PORT