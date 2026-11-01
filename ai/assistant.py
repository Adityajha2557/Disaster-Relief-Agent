
import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

MODEL_NAME = "gemini-flash-latest"


def ask_assistant(question, simulation_context):

    """
    Answer operator questions using current simulation data.

    Gemini explains the existing simulation results.
    It does not modify priorities or dispatch decisions.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing. "
            "Add it to your .env file."
        )

    if not question or not question.strip():
        return "Please enter a question."

    # Convert simulation information into JSON
    context_json = json.dumps(
        simulation_context,
        indent=2,
        default=str
    )

    # Limit context size
    context_json = context_json[:16000]

    prompt = f"""
You are the AI operations assistant for DRRAA
(Disaster Relief Resource Allocation Agent).

Your responsibilities:
1. Explain disaster simulation results.
2. Identify villages requiring urgent attention.
3. Explain vehicle allocation recommendations.
4. Explain resource shortages and shipments.
5. Summarize dynamic disaster events.
6. Provide clear, concise operational insights.

Important rules:
- Use only the supplied simulation data.
- Do not invent villages, quantities, vehicles or events.
- Clearly identify information based on simulation assumptions.
- The dataset is synthetic and AI-generated.
- Resource demand and camp inventory use illustrative assumptions.
- Do not claim that recommendations are real-world dispatch orders.
- Do not independently change allocation decisions.
- If information is missing, explicitly say so.

CURRENT SIMULATION DATA:

{context_json}

OPERATOR QUESTION:

{question}

Provide a clear answer using short sections or bullet points
where appropriate.
"""

    try:

        with genai.Client(api_key=api_key) as client:

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

        if not response.text:
            return "The AI assistant returned an empty response."

        return response.text

    except Exception as error:

        raise RuntimeError(
            f"Gemini assistant failed: {error}"
        ) from error
