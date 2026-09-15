FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agrogasm.py .
ENV AGROGASM_DB=/data/agrogasm.db
EXPOSE 5000
CMD ["sh", "-c", "flask --app agrogasm init-db && gunicorn -w 2 -b 0.0.0.0:5000 agrogasm:app"]
