import os
import json
import pdfplumber
import numpy as np
from collections import defaultdict

def extract_title(page):
    top_area = page.crop((0, 0, page.width, page.height * 0.2))
    words = top_area.extract_words(
        keep_blank_chars=False,
        extra_attrs=["size"],
        use_text_flow=True
    )
    if not words:
        return ""
    
    font_sizes = [w["size"] for w in words]
    max_size = max(font_sizes) if font_sizes else 0
    title_words = [w["text"] for w in words if w["size"] == max_size]
    return "".join(title_words).strip()

def process_page(page):
    words = page.extract_words(
        keep_blank_chars=False,
        extra_attrs=["size"],
        use_text_flow=True
    )
    if not words:
        return [], 0
    
    size_counter = defaultdict(int)
    for word in words:
        size_counter[round(word["size"], 1)] += 1
    body_size = max(size_counter.items(), key=lambda x: x[1])[0] if size_counter else 0

    lines = defaultdict(list)
    for word in words:
        line_key = round(word["top"] / 5) * 5
        lines[line_key].append(word)
    
    candidates = []
    for line_key in sorted(lines.keys()):
        line_words = lines[line_key]
        line_words.sort(key=lambda w: w["x0"])
        
        text = "".join(w["text"] for w in line_words).strip()
        if not text or len(text) < 2:
            continue
            
        avg_size = sum(w["size"] for w in line_words) / len(line_words)
        min_top = min(w["top"] for w in line_words)
        
        is_large_font = avg_size >= body_size * 1.5
        is_top_position = min_top < page.height * 0.15
        
        if is_large_font or is_top_position:
            candidates.append({
                "text": text,
                "size": avg_size,
                "top": min_top,
                "page": page.page_number
            })
    
    return candidates, body_size

def assign_levels(candidates):
    if not candidates:
        return []
    
    sizes = [c["size"] for c in candidates]
    if len(sizes) < 3:
        for i, c in enumerate(candidates):
            c["level"] = f"H{min(i+1, 3)}"
        return candidates
    
    q33 = np.quantile(sizes, 0.33)
    q66 = np.quantile(sizes, 0.66)
    
    for c in candidates:
        if c["size"] >= q66:
            c["level"] = "H1"
        elif c["size"] >= q33:
            c["level"] = "H2"
        else:
            c["level"] = "H3"
    
    return candidates

def process_pdf(path):
    with pdfplumber.open(path) as pdf:
        title = extract_title(pdf.pages[0]) if pdf.pages else ""
        
        all_candidates = []
        for page in pdf.pages:
            candidates, _ = process_page(page)
            all_candidates.extend(candidates)
        
        headings = assign_levels(all_candidates)
        headings.sort(key=lambda x: (x["page"], x["top"]))
        
        return {
            "title": title,
            "outline": [
                {"level": h["level"], "text": h["text"], "page": h["page"]}
                for h in headings
            ]
        }

if __name__ == "__main__":
    INPUT_DIR = "/app/input"
    OUTPUT_DIR = "/app/output"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    processed_count = 0
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            result = process_pdf(pdf_path)
            
            output_filename = f"{os.path.splitext(filename)[0]}.json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            processed_count += 1
    
    if processed_count == 0:
        with open(os.path.join(OUTPUT_DIR, "output.json"), "w") as f:
            json.dump({"title": "", "outline": []}, f)