FROM python:3.7.9-slim

WORKDIR /app

COPY . .

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "runner.py"]
