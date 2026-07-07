"""
llm.py

Responsible for:
- Connecting to Gemini
- Building prompts
- Generating answers from retrieved document chunks
"""

import os

from dotenv import load_dotenv
import google.generativeai as genai

from config import GEMINI_MODEL
from utils.citation_utils import format_citation
from utils.prompts import SYSTEM_PROMPT

# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Please add it to your .env file."
    )

genai.configure(api_key=api_key)

# ==========================================================
# Gemini Model
# ==========================================================

model = genai.GenerativeModel(GEMINI_MODEL)


# ==========================================================
# Generate Answer
# ==========================================================

def generate_answer(question, retrieved_chunks):
    """
    Generate an answer using Gemini.

    Args:
        question (str)
        retrieved_chunks (list)

    Returns:
        tuple:
            (answer, citations)
    """

    # No retrieved chunks
    if not retrieved_chunks:

        return (
            "The uploaded documents do not contain enough information to answer this question.",
            []
        )

    context = []

    citations = []

    for chunk in retrieved_chunks:

        context.append(
            f"""
Document: {chunk['document']}
Page: {chunk['page']}

{chunk['text']}
"""
        )

        citations.append(format_citation(chunk))

    context = "\n" + ("\n" + "=" * 60 + "\n").join(context)

    prompt = f"""
{SYSTEM_PROMPT}

========================
DOCUMENT CONTEXT
========================

{context}

========================
QUESTION
========================

{question}

========================
ANSWER
========================
"""

    try:

        response = model.generate_content(prompt)

        answer = response.text.strip()

    except Exception as e:

        answer = (
            "An error occurred while generating the answer.\n\n"
            f"{str(e)}"
        )

    if "do not contain enough information" in answer.lower():
        citations = []
    else:
        citations = sorted(set(citations))

    return answer, citations
