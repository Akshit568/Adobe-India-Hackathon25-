FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY process_pdfs.py .
ENTRYPOINT ["python", "process_pdfs.py", "--input-dir", "input", "--output-dir", "output"]
