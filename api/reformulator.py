from groq import Groq

def reformulate_query(original_query: str, top_chunks: list, groq_client: Groq) -> str:
    if not top_chunks:
        context_preview = "No relevant context was found in the documents at all."
    else:
        context_preview = "\n\n".join(top_chunks[:2])

    prompt = f"""The following query did not retrieve good context to answer it properly.

Original query: {original_query}

Context that WAS retrieved (but insufficient):
{context_preview}

Rewrite the query to be more specific or clearer, so it retrieves better matching content.
IMPORTANT: Do NOT invent names, companies, or details that are not mentioned in the context above.
If the context is empty or completely unrelated, rewrite the query using only more general/different phrasing of the ORIGINAL topic — do not add fabricated specifics.
Reply with ONLY the rewritten query, no explanation, no quotes.
"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
