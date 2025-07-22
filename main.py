import os
import json
import fitz
import pdfplumber
import joblib
import string

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

                    if len(text) < 3 or text.isspace():
                        continue

                    features = extract_features(text, size, font)
                    pred = encoder.inverse_transform(model.predict([features]))[0]

                    if pred in ["H1", "H2", "H3"]:
                        outline.append({
                            "level": pred,
                            "text": text,
                            "page": page_num
                        })
    return outline

def extract_title(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            words = first_page.extract_words(use_text_flow=True)
            if words:
                valid_words = [w for w in words if "size" in w and isinstance(w["size"], (int, float, str))]
                if not valid_words:
                    return "Untitled"
                title_line = max(valid_words, key=lambda w: float(w["size"]))
                return title_line["text"]
    except Exception as e:
        print("⚠️ Skipping title extraction due to error:", e)
        return "Untitled"

    return os.path.basename(pdf_path).replace(".pdf", "")


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
            with open(os.path.join(output_dir, filename.replace(".pdf", ".json")), "w") as f:
                json.dump(result, f, indent=2)

if __name__ == "__main__":
    input_dir = "/app/input"
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    model, encoder = load_model()
    process_all_pdfs(input_dir, output_dir, model, encoder)
