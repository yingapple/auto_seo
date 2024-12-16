import re
import json

def post_process(response: str) -> str:
    response = re.sub(r'^.*?\{', '{', response, flags=re.DOTALL).strip()
    cleaned_str = re.sub(r'^```json\s*', '', response)
    cleaned_str = re.sub(r'```$', '', cleaned_str).strip()
    return cleaned_str
