import os
import json
import fitz  # PyMuPDF
import pdfplumber
import joblib
import string
from difflib import SequenceMatcher

def load_model():
    model = joblib.load("heading_model.joblib")
    encoder = joblib.load("label_encoder.joblib")
    return model, encoder

def extract_features(text, size, font):
    return {
        "font_size": size,
        "bold": int("Bold" in font),
        "caps": sum(1 for c in text if c.isupper()) / max(len(text), 1),
        "length": len(text.split())
    }

def is_similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.9

def deduplicate_outline(outline):
    clean = []
    for entry in outline:
        if any(is_similar(entry["text"], prev["text"]) and entry["page"] == prev["page"] for prev in clean):
            continue
        clean.append(entry)
    return clean

def extract_outline(pdf_path, model, encoder):
    doc = fitz.open(pdf_path)
    outline = []

    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    font = span["font"]

                    # Skip junk or meaningless text
                    if (
                        len(text) < 3 or 
                        text.isspace() or 
                        all(c in string.punctuation for c in text) or
                        text.lower().startswith("page") or 
                        text.count('.') > 5 or 
                        text.lower().endswith("of")
                    ):
                        continue

                    features = extract_features(text, size, font)

                    # Predict and filter by confidence
                    proba = model.predict_proba([features])[0]
                    pred_idx = model.predict([features])[0]
                    pred_label = encoder.inverse_transform([pred_idx])[0]
                    confidence = max(proba)

                    if pred_label in ["H1", "H2", "H3"] and confidence > 0.6:
                        outline.append({
                            "level": pred_label,
                            "text": text,
                            "page": page_num
                        })

    return deduplicate_outline(outline)

def extract_title(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            words = first_page.extract_words(use_text_flow=True)
            if words:
                words = sorted(words, key=lambda w: -w.get("size", 0))
                for word in words:
                    text = word.get("text", "").strip()
                    if len(text) > 5 and not text.isspace() and not text.isnumeric():
                        return text
    except Exception as e:
        print("⚠️ Title extraction failed:", e)

    return "Untitled"

def process_all_pdfs(input_dir, output_dir, model, encoder):
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(input_dir, filename)
            title = extract_title(path)
            outline = extract_outline(path, model, encoder)
            result = {
                "title": title,
                "outline": outline
            }
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_dir = "sample_dataset/pdfs"
    output_dir = "sample_dataset/outputs"
    os.makedirs(output_dir, exist_ok=True)
    model, encoder = load_model()
    process_all_pdfs(input_dir, output_dir, model, encoder)