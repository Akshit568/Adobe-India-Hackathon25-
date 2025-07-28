# Challenge 1A – Multilingual PDF Processing Pipeline

> Build a robust, end‑to‑end PDF ingestion and processing system that can handle documents in any language.

---

## 📝 About This Project

This repository implements **Challenge 1A** of the Adobe India Hackathon 2025. It provides a fully automated pipeline to:

1. **Ingest** PDF files from a directory.
2. **Detect & extract** both text and images—regardless of the document’s language.
3. **Normalize & save** output in structured formats (plain text, JSON with metadata, images).

Everything runs as a standalone Python script, so you can drop in your own PDFs and get clean, ready‑to‑use data in seconds.

---

## 🔍 Key Features

- **Multilingual Support**  
  Utilizes OCR and language‑detection libraries to process PDFs in English, Hindi, French, Chinese—even right‑to‑left scripts like Arabic.

- **Text & Image Extraction**  
  Separately extracts text streams and embedded images, preserving layout metadata (page number, bounding boxes).

- **Configurable Output**  
  Choose between raw text dumps, JSON summaries, or exporting images to disk in organized folders.

- **Standalone & Lightweight**  
  Based on Python 3.11 with a minimal set of dependencies—no heavyweight frameworks required.

---

## 🚀 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/Akshit568/Adobe-India-Hackathon25-.git
   cd Adobe-India-Hackathon25-/challenge_1a
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the processor

bash
Copy
Edit
python process_pdfs.py \
  --input-dir    ./input_pdfs \
  --output-dir   ./output_data \
  --lang-detect  true
Inspect results

output_data/text/ — plain .txt files

output_data/json/ — page‑level JSON with metadata

output_data/images/ — all embedded figures

🛠️ How It Works
File Watcher
Scans the input_pdfs/ folder and queues any new PDFs.

OCR & Parsing

Uses pdfplumber for text streams

Falls back to pytesseract OCR for scanned pages

Detects language with langdetect for optimized OCR settings

Output Organizer
Saves everything to clearly named sub‑folders so downstream tools can pick up exactly what they need.

👤 Sole Contributor
This entire pipeline—from core logic to test cases and documentation—was designed and implemented end‑to‑end by Akshit Thakur.

📫 Contact
Feel free to open an issue if you run into any bugs or want to suggest new features!

Email: akshit.thakur@example.com
LinkedIn: Akshit Thakur

pgsql
Copy
Edit

Feel free to tweak any paths, examples or commands to match your actual scripts and folders!
::contentReference[oaicite:0]{index=0}
