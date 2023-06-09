FROM python:3.10-bullseye

WORKDIR /env

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ /env/app/
COPY setup.py .
RUN pip install -e .

WORKDIR /env/app/web
COPY config.yaml .

CMD ["/bin/sh", "-c", "./start.sh"]
