import re

def cut_reasoning(string: str):
    return re.sub(r'<think>.*?</think>', '', string, flags=re.DOTALL).strip()

def clean_text(text: str) -> str:
    # Keep letters, numbers, spaces, and basic punctuation
    return re.sub(r'[^a-zA-Z0-9\s.,!?;:()\-]', '', text)