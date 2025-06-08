import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def rewrite_query(user_query):
    prompt = f"""You are a Defence Training Assistant.
Rewrite the following into a clear, grammatically correct DSAT-related question:

Input: "{user_query}"

Output:"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=50,
        temperature=0.2
    )
    return response.choices[0].message['content'].strip()

