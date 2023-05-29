FROM python:3.10

WORKDIR /env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ /env/app/
COPY setup.py .
RUN pip install -e .

WORKDIR /env/app
COPY config.yaml .

CMD ["python", "stream/main.py", "-c", "config.yaml"]
