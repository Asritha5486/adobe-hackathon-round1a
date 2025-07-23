# PDF Heading Extractor – Adobe Hackathon Round 1A Submission

This project is part of Adobe India Hackathon 2025 – “Connecting the Dots” Challenge Round 1A.

## 🚀 Objective

The goal is to extract document structure (headings and title) from unstructured PDFs using:

- PDF parsing libraries (PyMuPDF, pdfplumber)
- A lightweight ML model (≤ 200MB)
- Dockerized pipeline for submission

## 📁 Project Structure

```
pdf_heading_extractor_final_1/
├── input/                   # Input PDF files (mounted at runtime)
├── output/                  # Output JSON files with headings and title
├── main.py                  # Main script to process PDFs
├── requirements.txt         # Python dependencies
├── heading_model.joblib     # Trained ML model (≤200MB)
├── label_encoder.joblib     # Label encoder for heading levels
├── Dockerfile               # Docker build file
└── README.md                # Project documentation
```

## 🧠 Features Extracted for ML

- Font size
- Bold or not
- Capitalization ratio
- Number of words

The model classifies lines into heading levels: H1, H2, H3

## 🐳 Docker Usage

1. Build the Docker image:

```bash
docker build -t adobe_challenge:asritha .
```

2. Run the container:

```bash
docker run --rm -v %cd%\input:/app/input -v %cd%\output:/app/output --network none adobe_challenge:asritha
```

On Linux/macOS, replace %cd% with $(pwd)

## 📝 Output Format

Each output JSON file contains:

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "Methodology", "page": 2 }
  ]
}
```

## 👩‍💻 Built With

- Python 3.9
- PyMuPDF
- pdfplumber
- scikit-learn
- Docker

## 🙋‍♀️ Team

Asritha Chunduri  
chasritha33@gmail.com
GitHub: [Asritha5486](https://github.com/Asritha5486)
