FROM python:3.11-slim

WORKDIR /app

COPY *.py requirements.txt config.json troncon_rva_support_fcd.json ./
ADD templates templates
ADD static static

RUN pip install --no-cache-dir -r requirements.txt
