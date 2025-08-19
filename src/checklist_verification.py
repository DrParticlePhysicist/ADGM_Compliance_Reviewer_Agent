import json
from Vectorstore_utils import search_Vectorstore
from LLM_client import get_LLM


def safe_json_loads(data, fallback=None):
    try:
        if isinstance(data, str):
            return json.loads(data)
        return data
    except Exception:
        return fallback if fallback is not None else data


def verify_checklist_dynamic(process_name, doc_types, kb_chunks=None, top_k=3):
    if kb_chunks is None:
        kb_chunks_raw = search_Vectorstore(process_name, top_k=top_k)
        kb_chunks = [c["text"] for c in kb_chunks_raw if c.get("text")]
    else:
        kb_chunks = kb_chunks

    uploaded_doc_types = set(x.lower().strip() for x in doc_types.values())

    prompt = f"""
Process: {process_name}

Known doc types mapping (filename -> type):
{json.dumps(doc_types, ensure_ascii=False)}

Uploaded document types list:
{json.dumps(list(doc_types.values()), ensure_ascii=False)}

Relevant KB context:
{json.dumps(kb_chunks[:3], indent=2, ensure_ascii=False)}

Task:
Based on the above KB context and uploaded documents, create only two lists:
1. required: List all documents required for this process. The required list must contain at least one entry from uploaded docs.
2. missing: List those from the required list that are NOT present in the uploaded doc types (case and whitespace insensitive comparison).

IMPORTANT:
- Do not include uploaded docs as missing.
- missing must always be a proper subset of required and contain ONLY those that are required but not uploaded.
- Do not just copy uploaded, required, or missing lists as-is; think carefully and deduplicate.
- If something is both uploaded and required, only include it in required, not in missing.
- missing must contain what is in requred but not present in uploaded. 
- missng and required list cant be same. 
- Return ONLY valid JSON with fields: {{"required": [...], "missing": [...]}}

"""

    llm_resp = get_LLM().invoke(prompt)
    llm_json = safe_json_loads(llm_resp, fallback={})

    required_list = [
        x.strip() for x in llm_json.get("required", [])
        if x and isinstance(x, str)
    ]
    missing_list = [
        req for req in required_list
        if req.lower().strip() not in uploaded_doc_types
    ]

    return json.dumps({"required": required_list, "missing": missing_list}, ensure_ascii=False)
