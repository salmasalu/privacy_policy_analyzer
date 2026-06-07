from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# Classify clause type

def _stage1_classify(clause: str) -> str:
    """
    Identifies what kind of data practice this clause describes.
    Feeds into Stage 2 as context.
    """
    prompt = f"""You are a privacy law analyst.
Identify the data practice in this clause in ONE short phrase (max 8 words).
Examples: "sells data to advertisers", "tracks location indefinitely", "shares with third parties"

Clause: "{clause}"

Respond with only the phrase, nothing else."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=30
    )
    return response.choices[0].message.content.strip()

# Assess risk with reasoning


def _stage2_assess(clause: str, practice: str) -> str:
    """
    Given the identified practice, explains why it is risky.
    Uses practice label from Stage 1 as grounding context.
    """
    prompt = f"""You are a privacy risk assessor.
This clause involves: {practice}

Explain in exactly 2 sentences:
1. Why this is a privacy risk
2. What user data is affected

Clause: "{clause}"

Be specific. No bullet points. Max 50 words total."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=80
    )
    return response.choices[0].message.content.strip()



# Suggest remediation


def _stage3_remediate(practice: str, assessment: str) -> str:
    """
    Generates a concrete user action based on the risk assessment.
    Closes the reasoning chain with actionable output.
    """
    prompt = f"""You are a privacy advisor.
Risk identified: {practice}
Assessment: {assessment}

Give ONE specific action a user can take to protect themselves.
Max 20 words. Start with a verb. Example: "Opt out of data sharing in Settings > Privacy > Data Sharing." """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=40
    )
    return response.choices[0].message.content.strip()

# MAIN ENTRY POINT 

def explain_risk(clause: str) -> str:
    """
    3-stage LLM reasoning chain:
    Stage 1 → classify what practice the clause describes
    Stage 2 → assess why it is a privacy risk
    Stage 3 → suggest a concrete user remediation action

    Design decision:
    - Single-call LLM (old version) mixed classification + explanation
      in one prompt, producing inconsistent output structure.
    - Chained approach grounds each stage on the previous output,
      improving coherence and making each stage independently testable.
    - Trade-off: 3x API calls per clause vs 1x. Mitigated by the
      40-clause limit in classifier.py and URL-level caching in routes.py.
    """
    try:
        practice = _stage1_classify(clause)
        assessment = _stage2_assess(clause, practice)
        remediation = _stage3_remediate(practice, assessment)

        return (
            f"Practice: {practice}\n"
            f"Risk: {assessment}\n"
            f"Action: {remediation}"
        )

    except Exception as e:
        return f"Analysis unavailable: {str(e)}"