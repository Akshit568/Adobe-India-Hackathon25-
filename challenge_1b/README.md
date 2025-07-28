# Challenge 1B – Scalable PDF Processing Service

> Extend your PDF ingestion pipeline into a fully containerized, API‑driven microservice.

---

## 📝 About This Project

This directory implements **Challenge 1B** of the Adobe India Hackathon 2025. Building on your offline PDF pipeline (Challenge 1A), here you’ll find:

- A **RESTful API** for submitting PDF jobs on‑the‑fly  
- A **worker pool** for concurrent processing  
- **Docker** and **Docker Compose** configurations for easy deployment  

This service accepts PDFs in any language, leverages OCR under the hood, and returns clean text, structured JSON metadata, and extracted images with a single HTTP call.

---

## 🔍 Key Features

- **HTTP API Endpoint**  
  Submit PDFs (multipart/form‑data) to `/process` and receive a job ID immediately.

- **Asynchronous Processing**  
  Jobs are queued and processed by a configurable pool of worker threads or processes, so you never block your client.

- **Multilingual OCR & Layout Analysis**  
  Supports Hindi, English, Chinese, Arabic… whatever you throw at it, it’ll extract text and image regions with page‑level metadata preserved.

- **Docker‑Ready**  
  - `Dockerfile` ensures a minimal Python 3.11 image with all dependencies.  
  - `docker-compose.yml` spins up the API service plus a Redis queue backend.

- **Health Checks & Metrics**  
  Built‑in `/health` and `/metrics` endpoints for uptime, queue depth, and throughput monitoring.

---

## 🚀 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Akshit568/Adobe-India-Hackathon25-.git
   cd Adobe-India-Hackathon25-/challenge_1b
Build & run with Docker Compose

bash
Copy
Edit
docker-compose up --build
Submit a PDF

bash
Copy
Edit
curl -F "file=@./input/sample.pdf" http://localhost:8000/process
# → { "job_id": "1234-abcd" }
Poll for results

bash
Copy
Edit
curl http://localhost:8000/results/1234-abcd
# → {"status":"done","text_url":"/outputs/text/1234-abcd.txt",…}
🛠️ How It Works
API Layer

Built with FastAPI (or Flask)

Validates uploads & returns job IDs

Queue & Workers

Redis (via docker-compose.yml) for job queuing

Worker script listens, picks up jobs, and invokes the PDF processor

Processing Pipeline

Reuses your pdfplumber + pytesseract logic

Language detection via langdetect for optimized OCR

Outputs structured files under ./outputs/

Containerization

Single Docker image for both API & worker

Environment variables to tweak concurrency, timeouts, etc.

👤 Sole Contributor
All core logic, API design, Docker orchestration, tests, and documentation were crafted end‑to‑end by Akshit Thakur.

📫 Contact
Questions or feature requests? Open an issue or reach out:

Email: akshit.thakur@example.com

LinkedIn: Akshit Thakur

makefile
Copy
Edit
::contentReference[oaicite:0]{index=0}








Sources

Ask ChatGPT

