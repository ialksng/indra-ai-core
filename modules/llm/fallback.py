from modules.llm.local_model import local_generate
from modules.llm.hf_model import hf_generate

def generate_with_fallback(prompt, use_external=False):
    if use_external:
        try:
            return hf_generate(prompt)
        except:
            return local_generate(prompt)
    else:
        return local_generate(prompt)