AI_KEYWORDS = [
    "AI", "Artificial Intelligence", "Machine Learning", "ML",
    "NLP", "Data Scientist", "Deep Learning", "LLM", "GenAI"
]

def is_ai_job(title):
    return any(term.lower() in title.lower() for term in AI_KEYWORDS)
