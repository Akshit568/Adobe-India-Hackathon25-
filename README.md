# Adobe-India-Hackathon25-

Adobe India Hackathon 2025 – Connecting the Dots

Rethink Reading. Rediscover Knowledge.Transform static PDFs into an intelligent, interactive, and multilingual research companion.



📖 Table of Contents

Overview

My Contributions

Key Features

Repository Structure

Challenge 1a: PDF Processing Solution

Challenge 1b: Multi-Collection Analysis

Technologies

Contributing

License

🧐 Overview

In the “Connecting the Dots” project, we reimagine the humble PDF as an intelligent, interactive, and multilingual research experience. Our solution:

Extracts structured outlines, headings, and metadata from PDFs.

Connects semantic insights across single or multiple documents.

Supports PDFs in any language—English, Hindi, French, Spanish, Mandarin, and more—leveraging robust NLP pipelines.

Delivers both command-line tools and Jupyter notebooks for flexible analysis.

Whether you’re a data scientist, researcher, or student, this project enables you to surface key concepts and cross-document connections at lightning speed.

🛠️ My Contributions

As the sole developer on this project, I designed and implemented every component:

Custom PDF Parser: Wrote process_pdfs.py using pdfminer.six and PyPDF2 to extract document sections, headings, and metadata with high accuracy.

Language Detection & OCR: Integrated Tesseract OCR coupled with a language-detection module to automatically handle scanned pages and support multilingual text.

Docker Containerization: Created a Dockerfile to ensure reproducible environments, simplifying deployment across machines.

Semantic Linking Module: Developed multi_collection.py leveraging SentenceTransformers embeddings to identify and visualize cross-document topic connections.

Interactive Analysis Notebook: Authored analysis.ipynb with step-by-step visualizations using matplotlib and networkx to highlight persona-based insights.

✨ Key Features

🔍 Structure Extraction: Parses headings, subheadings, and table of contents.

🌐 Multilingual Processing: Auto-detects document language and applies language-specific NLP pipelines.

⚡ Fast & Lightweight: Dockerized for ease of deployment and consistent runs.

👥 Persona-Based Insights: Tag and group content relevant to different user personas (students, researchers, developers).

🔗 Cross-Document Linking: Visualizes semantic connections across multiple PDFs.

📊 Interactive Notebooks: Jupyter notebooks demonstrating end-to-end analysis.

🗂️ Repository Structure

Adobe-India-Hackathon25-/
├── Challenge_1a/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── process_pdfs.py
│   └── README.md
├── Challenge_1b/
│   ├── data/
│   │   └── sample_pdfs/
│   ├── analysis.ipynb
│   ├── multi_collection.py
│   └── README.md
├── .gitignore
└── README.md

🚀 Challenge 1a: PDF Processing Solution

Features

🔍 Structure Extraction: Parses section headings, subheadings, and table of contents.

🌐 Language Detection & OCR: Automatically identifies document language and applies OCR for scanned pages.

📦 Output Schema: Generates JSON files with sections, page mappings, language tags, and metadata.

Getting Started

Clone the repo

git clone https://github.com/Akshit568/Adobe-India-Hackathon25-.git
cd Adobe-India-Hackathon25-

Build the Docker image

cd Challenge_1a
docker build -t pdf-processor .

Run the processor

docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  pdf-processor

Input: Place your PDFs in Challenge_1a/input/

Output: Structured JSON in Challenge_1a/output/

🔬 Challenge 1b: Multi-Collection Analysis

Features

👥 Persona-Based Insights: Tag and group content relevant to different user personas.

🔗 Cross-Document Linking: Finds and visualizes semantic connections across multiple PDFs.

📊 Notebook Walkthrough: Interactive Jupyter notebook demonstrating analysis, visualizations, and link graphs.

Usage

Install dependencies

pip install -r Challenge_1b/requirements.txt

Run the analysis script

python Challenge_1b/multi_collection.py \
  --data-dir Challenge_1b/data/sample_pdfs \
  --output-dir Challenge_1b/results

Explore the Jupyter notebook

cd Challenge_1b
jupyter notebook analysis.ipynb

🛠️ Technologies

Language: Python 3.11

Containerization: Docker

Libraries:

PDF parsing: PyPDF2, pdfminer.six

OCR: Tesseract via pytesseract

NLP & embeddings: spaCy, Transformers, SentenceTransformers

Data processing: pandas, NumPy

Visualization: matplotlib, networkx

🤝 Contributing

Contributions, issues, and feature requests are welcome!To contribute:

Fork the repo

Create a branch (git checkout -b feature-name)

Commit your changes (git commit -m 'Add new feature')

Push to the branch (git push origin feature-name)

Open a Pull Request

📄 License

This project is licensed under the MIT License.Feel free to use, modify, and distribute—just give appropriate credit.

Built with ❤️ for Adobe India Hackathon 2025.

