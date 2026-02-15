FROM python:3.11-slim
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "endpoint:app", "--host", "0.0.0.0", "--port", "8080"]
EXPOSE 8080