# src/process_identifier.py
import json
from Vectorstore_utils import search_Vectorstore
from LLM_client import get_LLM

def summarize_doc_with_kb(doc_text, filename, top_k=3):
    kb_chunks_raw = search_Vectorstore(doc_text, top_k=top_k)
    kb_context_texts = [c["text"] for c in kb_chunks_raw if c.get("text")]

    prompt = f"""
Summarize the following document for ADGM compliance review.

Document: {filename}

Relevant Knowledge Base context:
{json.dumps(kb_context_texts, indent=2, ensure_ascii=False)}

Document content excerpt:
{doc_text}

Focus on details and the part it is relevant to the Knowledge base.
List which tasks/process/procedure in ADGM paradigm the given docs are required for, 
and provide every important information to help process identification.

Provide a concise summary (max 200 words) and based on Knowledge base and do not include filename to use as information to make summary, as filename can be wrong and misleading.
"""
    return get_LLM().invoke(prompt)

def identify_process_from_summaries(summaries_dict):
    doc_blocks = "\n\n".join(f"{fname}: {summ}" for fname, summ in summaries_dict.items())

    prompt = f"""
You are an ADGM legal expert.

Based on the document summaries below, identify :
1. The overall process (e.g., company incorporation, license renewal, etc.)
2. The type of each document
3. A good enough summary of the process identified with rich information density specialy biased towards the discussion of different documents that are generally required by the identified process. 
Return ONLY valid JSON:
{{
  "process": "<process_name>",
  "doc_types": {{"filename": "<doc_type>"}},
  "process_summary":"" 
}}

Summaries:
{doc_blocks}
"""
    return get_LLM().invoke(prompt)
