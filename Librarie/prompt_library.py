def explain_topic(topic):
    return f"""
    Explain the following programming topic:
    Topic: {topic}
    Include:
    1. A simple definition
    2. Why it is used
    3. How it works
    4. One practical example
    5. One common mistake
    Keep the explanation beginner-friendly.
    """

def review_code(code):
    return f"""
    Review the following Python code:
    {code}
    Identify:
    1. Errors or bugs
    2. Bad practices
    3. Possible improvements
    For every issue, explain why it is a problem.
    Do not rewrite the entire code unless necessary.
    """

def summarize_text(text):
    return f"""
    Summarize the following text:
    {text}
    Requirements:
    - Keep the summary concise.
    - Include only important information.
    - Return the key points as bullet points.
    - Do not add information that is not present in the text.
    """

def generate_interview_question(topic, difficulty="beginner"):
    return f"""
    Generate one {difficulty}-level technical interview question
    about {topic}.
    Do not provide the answer.
    Return only one question.
    """

def answer_from_context(question, relevant_chunks):
    prompt = "Context Information:\n"
    for i, chunk in enumerate(relevant_chunks):
        prompt += f"--- Chunk {i+1} ---\n{chunk[1]}\n\n"
    prompt += f"""User Question:
{question}

Instructions:
- Provide a well-structured, clear answer based strictly on the context provided above.
- Structure the response with appropriate Markdown (headers, bullet points, bold key phrases, or code blocks) for maximum clarity and readability.
- If the answer cannot be determined from the context, state: "I don't know based on the provided context."
"""
    return prompt
