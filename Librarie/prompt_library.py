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
    # Format clinic records concisely
    context_text = ""
    if relevant_chunks:
        context_text = "\n".join([f"- Clinic Record {i+1}: {chunk[1]}" for i, chunk in enumerate(relevant_chunks)])
    else:
        context_text = "No clinic records available."

    prompt = f"""Clinic Information Records:
{context_text}

Caller's Spoken Query:
"{question}"

Instructions for Spoken Response:
- Speak directly to the caller in 1 to 2 natural, warm sentences.
- If the caller says "hi", "hello", or introduces themselves, greet them warmly and ask how you can assist them today.
- Use the clinic records accurately if the question is about clinic services, doctors, timings, or policies.
- If the answer is not in the records, politely offer to connect them to the front desk or arrange a callback.
- DO NOT use markdown, bullet points, asterisks, or robotic phrases like "According to the context".
"""
    return prompt

