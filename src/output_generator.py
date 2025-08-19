# output_generator.py
# src/output_generator.py
import json
from pathlib import Path
from docx import Document
from typing import List, Dict

def save_reviewed_docx(original_path: Path, issues: List[Dict], output_path: Path):
    """
    Inline comments को insert कर के reviewed docx save करें
    (या पहले से बनी inline_commenter.py से call भी कर सकते हैं)
    """
    from inline_commenter import insert_comments
    insert_comments(original_path, issues, output_path)


def generate_summary_json(process_name: str, uploaded_docs: List[str], missing_docs: List[str], issues: List[Dict], output_path: Path):
    """
    Compliance check का summary structured JSON में बनाएं और save करें
    """
    summary = {
        "process": process_name,
        "documents_uploaded": len(uploaded_docs),
        "required_documents": len(uploaded_docs) + len(missing_docs),
        "missing_documents": missing_docs,
        "issues_found": issues
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)
