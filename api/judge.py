from groq import Groq
import json
import re


def check_grounding(query: str, top_chunks: list, answer: str, groq_client: Groq) -> dict:
    context = "\n\n".join(top_chunks)

    prompt = f"""You are a strict evaluator. Judge if the ANSWER is fully supported by the CONTEXT below.

Context:
{context}

Question: {query}

Answer: {answer}

Rate how well the answer is grounded in the context, from 1 to 5:
5 = fully supported, every claim traceable to context
3 = partially supported, some claims not in context
1 = not supported at all, answer is unrelated or fabricated

Reply with ONLY valid JSON, no other text:
{{"score": <1-5 integer>, "reason": "<one short sentence>"}}
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        result = json.loads(raw)
        return {"score": int(result["score"]), "reason": result.get("reason", "")}
    except (json.JSONDecodeError, KeyError, ValueError):
        return {"score": 1, "reason": f"Judge parsing failed. Raw output: {raw}"}