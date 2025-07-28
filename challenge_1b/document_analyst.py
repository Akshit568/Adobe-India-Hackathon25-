import PyPDF2
import os
import json
import re
from datetime import datetime
from collections import Counter
from langdetect import detect, DetectorFactory
import sys

# Set a seed for langdetect for consistent results (optional, but good for reproducibility)
DetectorFactory.seed = 0 

# --- Configuration ---
# Minimum length for a text block to be considered a significant 'section'
MIN_SECTION_LENGTH = 50
# Minimum length for a text block to be considered a 'sub-section' (e.g., a paragraph)
MIN_SUBSECTION_LENGTH = 20
# Maximum number of words for a line to be considered a potential section title
MAX_TITLE_WORDS = 10

# Global dictionary to store loaded stopwords for different languages
LOADED_STOP_WORDS = {}

# --- Multilingual NLP Components (Imported conditionally) ---
try:
    from janome.tokenizer import Tokenizer as JanomeTokenizer
    JANOME_T = JanomeTokenizer()
    JANOME_AVAILABLE = True
except ImportError:
    print("Warning: Janome not found. Japanese tokenization will be basic.", file=sys.stderr)
    JANOME_AVAILABLE = False

try:
    from pecab import PeCab
    PECAB_T = PeCab()
    PECAB_AVAILABLE = True
except ImportError:
    print("Warning: Pecab not found. Korean tokenization will be basic.", file=sys.stderr)
    PECAB_AVAILABLE = False

def load_stopwords(lang_code, stopwords_dir="lang_data"):
    """
    Loads language-specific stopwords from a file.
    Caches loaded stopwords to avoid re-reading files.
    """
    if lang_code in LOADED_STOP_WORDS:
        return LOADED_STOP_WORDS[lang_code]

    filepath = os.path.join(stopwords_dir, f"stopwords_{lang_code}.txt")
    if not os.path.exists(filepath):
        print(f"Warning: Stopwords file not found for {lang_code} at {filepath}. Continuing without stop words for this language.", file=sys.stderr)
        return set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().splitlines())
    
    LOADED_STOP_WORDS[lang_code] = stopwords
    return stopwords

# --- Text Processing Utilities ---
def multilingual_tokenize(text, lang_code):
    """
    Tokenizes text based on language.
    """
    if lang_code == 'ja' and JANOME_AVAILABLE:
        # For Japanese, use Janome morphological analysis
        return [token.surface for token in JANOME_T.tokenize(text)]
    elif lang_code == 'ko' and PECAB_AVAILABLE:
        # For Korean, use Pecab morphological analysis
        return [token[0] for token in PECAB_T.morphs(text)]
    else:
        # Default to whitespace tokenization for other languages (e.g., en, fr, ro)
        return text.split()

def preprocess_text(text):
    """
    Cleans, tokenizes, and removes language-specific stop words from text.
    Automatically detects language.
    """
    if not text.strip(): # Handle empty or whitespace-only text
        return []

    try:
        lang_code = detect(text)
    except Exception: # langdetect can fail for very short/ambiguous strings
        lang_code = 'en' # Default to English if detection fails
        # print(f"Warning: Language detection failed for '{text[:50]}...'. Defaulting to English.", file=sys.stderr)

    stopwords = load_stopwords(lang_code)

    # Replace common newline patterns with a single space for consistent tokenization
    text = text.lower()
    text = text.replace('\r\n', ' ').replace('\n', ' ')
    
    # --- ADDED: Robust handling of problematic Unicode characters ---
    # This attempts to encode the text to UTF-8 and ignore any characters
    # that cannot be encoded (like malformed surrogates), then decode it back.
    # This strips out problematic Unicode sequences that cause encoding errors.
    text = text.encode('utf-8', errors='ignore').decode('utf-8')

    # Remove any character that is not a Unicode word character or whitespace.
    # The re.UNICODE flag (re.U) makes \w (word character) and \s (whitespace) Unicode-aware.
    # This should correctly preserve Japanese/Korean/Chinese characters as well as Latin alphabet and numbers.
    text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)

    tokens = multilingual_tokenize(text, lang_code)
    
    # Filter out empty tokens and stopwords
    return [word for word in tokens if word and word not in stopwords]

def calculate_relevance_score(text_tokens, query_tokens):
    """
    Calculates a simple relevance score based on the overlap of keywords.
    The score is the count of query tokens found in the text tokens, normalized
    by the length of the text block.
    """
    if not text_tokens or not query_tokens:
        return 0.0

    score = 0
    query_tokens_set = set(query_tokens)
    
    for token in text_tokens:
        if token in query_tokens_set:
            score += 1
            
    # Normalize the score by the number of tokens in the text block
    normalized_score = score / (len(text_tokens) + 1e-6) # Add small epsilon to prevent division by zero
    
    return normalized_score

# --- PDF Processing ---
def extract_text_from_pdf(pdf_path):
    """
    Extracts text page by page from a PDF and attempts to segment it into
    logical blocks (potential sections or paragraphs).
    
    Returns a list of dictionaries, where each dictionary represents a block of text
    and includes its content, original page number, and a flag indicating if it's
    a potential title.
    """
    extracted_data = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                # Split text into lines to look for potential titles and paragraph breaks
                lines = text.split('\n')
                
                current_block_lines = []
                for i, line in enumerate(lines):
                    stripped_line = line.strip()
                    
                    # Heuristic to detect start of a new block or end of previous one.
                    # Consider multiple blank lines as a separator for distinct blocks.
                    # Also consider significant indentation changes or lines ending with specific punctuation
                    # as both are heuristic for block boundaries, though keeping it simple for now.
                    if not stripped_line and len(current_block_lines) > 0 and \
                       (i + 1 < len(lines) and not lines[i+1].strip()): # Two consecutive blank lines
                        block_text = "\n".join(current_block_lines).strip()
                        if block_text:
                            # Try to infer if the first line of the block is a title
                            first_line_of_block = current_block_lines[0].strip()
                            is_title_candidate = False
                            if first_line_of_block and len(first_line_of_block.split()) <= MAX_TITLE_WORDS:
                                is_title_candidate = True

                            extracted_data.append({
                                'text': block_text,
                                'page_number': page_num + 1,
                                'is_title_candidate': is_title_candidate,
                                'original_line': first_line_of_block if is_title_candidate else ""
                            })
                        current_block_lines = []
                        continue # Skip the blank line itself
                    
                    current_block_lines.append(line)
                
                # Add any remaining text in current_block_lines after the loop
                if current_block_lines:
                    block_text = "\n".join(current_block_lines).strip()
                    if block_text:
                        first_line_of_block = current_block_lines[0].strip()
                        is_title_candidate = False
                        if first_line_of_block and len(first_line_of_block.split()) <= MAX_TITLE_WORDS:
                            is_title_candidate = True
                        
                        extracted_data.append({
                            'text': block_text,
                            'page_number': page_num + 1,
                            'is_title_candidate': is_title_candidate,
                            'original_line': first_line_of_block if is_title_candidate else ""
                        })
                
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}", file=sys.stderr)
    return extracted_data

def analyze_documents(pdf_paths, persona, job_to_be_done):
    """
    Main function to orchestrate document analysis. It extracts content,
    calculates relevance, ranks sections, and formats the output as JSON.
    """
    processing_timestamp = datetime.now().isoformat()
    
    # Combine persona and job for query keywords, preprocess them multilingually
    query_text = f"{persona} {job_to_be_done}"
    query_tokens = preprocess_text(query_text)

    all_sections_data = [] # To hold data for 'extracted_sections'
    all_sub_sections_data = [] # To hold data for 'sub_section_analysis'

    for pdf_path in pdf_paths:
        document_name = os.path.basename(pdf_path)
        extracted_blocks = extract_text_from_pdf(pdf_path)
        
        document_sections_candidates = []

        # Step 1: Identify and rank potential sections from extracted blocks
        for i, block in enumerate(extracted_blocks):
            block_text = block['text']
            block_page = block['page_number']
            
            # Skip blocks that are too short to be meaningful sections
            if len(block_text) < MIN_SECTION_LENGTH:
                continue
            
            block_tokens = preprocess_text(block_text)
            relevance_score = calculate_relevance_score(block_tokens, query_tokens)
            
            # Determine section title based on heuristics or default
            section_title = f"Content Block {i+1} (Page {block_page})" 
            if block['is_title_candidate'] and block['original_line']:
                section_title = block['original_line']
            elif len(block_text.split('\n')[0].split()) <= MAX_TITLE_WORDS:
                 # If the first line of the block is short, use it as a title
                 section_title = block_text.split('\n')[0].strip()
            
            document_sections_candidates.append({
                "document": document_name,
                "page_number": block_page,
                "section_title": section_title,
                "relevance_score": relevance_score, # Temporarily store for sorting
                "full_text": block_text # Keep full text for sub-section analysis
            })
            
        # Sort candidate sections by relevance score in descending order
        document_sections_candidates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Assign importance_rank and prepare for final output
        for rank, section in enumerate(document_sections_candidates):
            all_sections_data.append({
                "document": section['document'],
                "page_number": section['page_number'],
                "section_title": section['section_title'],
                "importance_rank": rank + 1 # Ranks start from 1
            })
            
            # Step 2: Sub-section analysis for a limited number of top relevant sections
            # This balances detailed analysis with performance constraints.
            if rank < 5: # Process top 5 most relevant sections for sub-sections
                full_section_text = section['full_text']
                section_page = section['page_number']
                
                # Split the full section text into individual paragraphs or smaller chunks
                # assuming paragraphs are separated by two or more newlines.
                paragraphs = [p.strip() for p in full_section_text.split('\n\n') if p.strip()]
                
                for p_idx, paragraph in enumerate(paragraphs):
                    if len(paragraph) < MIN_SUBSECTION_LENGTH: # Skip very short paragraphs
                        continue
                        
                    paragraph_tokens = preprocess_text(paragraph)
                    sub_relevance_score = calculate_relevance_score(paragraph_tokens, query_tokens)
                    
                    if sub_relevance_score > 0.0: # Only include sub-sections that show some relevance
                        all_sub_sections_data.append({
                            "document": document_name,
                            "refined_text": paragraph,
                            # Outputting just page_number for simplicity as per user's earlier example
                            "page_number": section_page, 
                            "relevance_score": sub_relevance_score # Temporarily store for sorting
                        })
    
    # Sort all identified sub-sections by their relevance score globally
    all_sub_sections_data.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Clean up temporary fields before final JSON output
    final_extracted_sections = []
    for sec in all_sections_data:
        # Create a new dictionary to avoid modifying the original during iteration
        temp_sec = {k: v for k, v in sec.items() if k not in ['relevance_score', 'full_text']}
        final_extracted_sections.append(temp_sec)

    final_sub_section_analysis = []
    for sub_sec in all_sub_sections_data:
        temp_sub_sec = {k: v for k, v in sub_sec.items() if k != 'relevance_score'}
        final_sub_section_analysis.append(temp_sub_sec)

    # Construct the final JSON output structure
    output_json = {
        "metadata": {
            "input_documents": [os.path.basename(p) for p in pdf_paths],
            "persona": persona,
            "job_to_be_done": job_to_be_done,
            "processing_timestamp": processing_timestamp
        },
        "extracted_sections": final_extracted_sections,
        "sub_section_analysis": final_sub_section_analysis
    }

    return output_json

# --- Main Execution Block ---
if __name__ == "__main__":
    # Define input and output directories.
    # Docker mounts the local collection folder to /app/input
    input_dir = os.getenv('INPUT_DIR', '/app/input') 
    # Output is written back to the same mounted input folder as per hackathon standard
    output_dir = os.getenv('OUTPUT_DIR', '/app/input') 

    # Ensure the output directory exists. (It's the mounted input dir, so it should exist)
    os.makedirs(output_dir, exist_ok=True)

    # Path to the input JSON file (expected directly in the mounted input directory)
    input_json_filename = "challenge1b_input.json" 
    input_json_path = os.path.join(input_dir, input_json_filename)

    # Check if input.json exists
    if not os.path.exists(input_json_path):
        print(f"Error: {input_json_filename} not found in '{input_dir}'.", file=sys.stderr)
        print(f"Please ensure '{input_json_filename}' is present in the mounted input directory.", file=sys.stderr)
        exit(1)

    # Load input data from challenge1b_input.json
    try:
        with open(input_json_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Extract persona and job-to-be-done
        persona_role = input_data.get("persona", {}).get("role", "Unknown Persona")
        job_task = input_data.get("job_to_be_done", {}).get("task", "Unknown Task")

        # Construct list of PDF paths from the 'documents' array in input.json
        pdf_files_info = input_data.get("documents", [])
        pdf_paths = []
        # PDFs are expected in a 'PDFs' subfolder within the mounted input directory
        pdf_subfolder = os.path.join(input_dir, "PDFs") 

        if not os.path.exists(pdf_subfolder):
            print(f"Error: 'PDFs' subfolder not found in '{input_dir}'.", file=sys.stderr)
            print("Please ensure your PDF documents are placed in an 'PDFs' subfolder within the mounted input directory.", file=sys.stderr)
            exit(1)

        for doc_info in pdf_files_info:
            filename = doc_info.get("filename")
            if filename:
                full_pdf_path = os.path.join(pdf_subfolder, filename)
                if os.path.exists(full_pdf_path):
                    pdf_paths.append(full_pdf_path)
                else:
                    print(f"Warning: PDF file not found: '{full_pdf_path}'. It will be skipped.", file=sys.stderr)
            else:
                print(f"Warning: Document entry missing 'filename' in {input_json_filename}: {doc_info}", file=sys.stderr)

        if not pdf_paths:
            print(f"No valid PDF files found or specified in '{input_json_path}'. No analysis will be performed.", file=sys.stderr)
            exit(1)

        print(f"Found {len(pdf_paths)} PDF(s) to process based on {input_json_filename} in '{input_dir}'.")
        print(f"Persona: '{persona_role}'")
        print(f"Job to be done: '{job_task}'")
        
        # Call the main analysis function
        output_data = analyze_documents(pdf_paths, persona_role, job_task)
        
        # Define the output file path as specified by the hackathon (challenge1b_output.json)
        # It's written to the same mounted directory (e.g., Collection X folder)
        output_file_path = os.path.join(output_dir, "challenge1b_output.json")
        
        # Write the JSON output to the specified file
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False) # Use ensure_ascii=False for proper multilingual JSON output
        
        print(f"Analysis complete. Output saved to '{output_file_path}'.")

    except json.JSONDecodeError as e:
        print(f"Error decoding {input_json_filename}: {e}", file=sys.stderr)
        print(f"Please ensure '{input_json_filename}' is a valid JSON file.", file=sys.stderr)
        exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        exit(1)

