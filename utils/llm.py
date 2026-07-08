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

import config
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

model = genai.GenerativeModel(config.GEMINI_MODEL)


def _trim_context_text(text, max_chars=None):
    text = (text or "").strip()

    max_chars = max_chars or getattr(config, "MAX_CONTEXT_CHARS_PER_CHUNK", 900)

    if len(text) <= max_chars:
        return text

    return text[:max_chars].rsplit(" ", 1)[0].strip()


# ==========================================================
# Generate Research Response
# ==========================================================

def generate_answer(
    request,
    retrieved_chunks,
    task_label="Question Answering",
    task_instruction=None,
    max_output_tokens=None,
    max_context_chars=None,
    stream_callback=None,
):
    """
    Generate a research-assistance response using Gemini.

    Args:
        request (str)
        retrieved_chunks (list)
        task_label (str)
        task_instruction (str | None)
        max_output_tokens (int | None)
        max_context_chars (int | None)
        stream_callback (callable | None)

    Returns:
        tuple:
            (answer, citations)
    """

    # No retrieved chunks
    if not retrieved_chunks:

        return (
            "The uploaded documents do not contain enough information to answer this request.",
            []
        )

    context = []

    citations = []

    for chunk in retrieved_chunks:

        context.append(
            f"""
Document: {chunk['document']}
Page: {chunk['page']}

{_trim_context_text(chunk['text'], max_chars=max_context_chars)}
"""
        )

        citations.append(format_citation(chunk))

    context = "\n" + ("\n" + "=" * 60 + "\n").join(context)

    prompt = f"""
{SYSTEM_PROMPT}

========================
RESEARCH TASK
========================

Task type: {task_label}

Task instructions:
{task_instruction or "Answer the user's request using only the supplied document context."}

========================
DOCUMENT CONTEXT
========================

{context}

========================
USER REQUEST
========================

{request}

========================
RESEARCH ASSISTANCE RESPONSE
========================
"""

    try:

        generation_config = {
            "temperature": getattr(config, "GEMINI_TEMPERATURE", 0.2),
            "max_output_tokens": max_output_tokens or getattr(
                config,
                "GEMINI_MAX_OUTPUT_TOKENS",
                900
            ),
        }

        if stream_callback:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={
                    "timeout": getattr(config, "GEMINI_REQUEST_TIMEOUT_SECONDS", 12)
                },
                stream=True,
            )

            answer_parts = []

            for chunk in response:
                text = getattr(chunk, "text", "")

                if not text:
                    continue

                answer_parts.append(text)
                stream_callback("".join(answer_parts))

            answer = "".join(answer_parts).strip()

        else:
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                request_options={
                    "timeout": getattr(config, "GEMINI_REQUEST_TIMEOUT_SECONDS", 12)
                },
            )

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
