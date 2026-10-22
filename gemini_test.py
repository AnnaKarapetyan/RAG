from dotenv import load_dotenv
from google import genai
from retriever import retrieve
import re
import time

load_dotenv()
client = genai.Client()
Models = ["gemini-flash-lite-latest", "gemini-flash-latest"]
Threshold = 0.4

def ask_llm(prompt):
    for model in Models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                model=model,
                contents=prompt,
                )
                return response.text
            except Exception as e:
                print(f"{model}, attempt {attempt + 1}: {e}")
                time.sleep(2 * (attempt + 1))
    return None

def answer(question):
    result= retrieve(question, 8)
    if not result or result[0]["distance"] > Threshold:
        return {"answer": "Answer is not available in sources", "sources": [], "sources_used": []}
    parts = []
    sources = []
    for i,ch in enumerate(result):
       parts.append(f"[{i+1}] ({ch['url']}) \n {ch['text']}") 
       sources.append(ch['url'])
    content = "\n\n".join(parts)
    prompt = f"""You are a documentation assistant for the FastAPI framework.

Answer the user's question using ONLY the context below. The context consists of numbered excerpts from the official FastAPI documentation.

Rules:
1. Use only information from the context. Do not use your own knowledge, even if you know the answer.
2. If the context does not contain the answer, reply exactly: "I could not find this in the documentation." Do not guess.
3. Be concise and practical. If the answer involves code, include a short code example taken from the context.
4. Answer in the same language as the question.
5. At the end, add a line "Sources:" followed by the numbers of the excerpts you actually used , for example: Sources: [1], [3].Always write the word "Sources:" in English, even if you answer in another language. Do not list excerpts you did not use.

Context:
{content}

Question: {question}

Answer:"""
    text = ask_llm(prompt)
    if text is None:
        return {"answer": "Service is temporarily unavailable, try again later", "sources": sources, "sources_used": []}
    pieces = text.rsplit("Sources:", 1)
    if len(pieces) == 1:
        pieces = pieces[0].rsplit("Источники:", 1)
    Sources_used_N =[]
    if len(pieces) == 2:
        Sources_used_N = [int(n) - 1 for n in re.findall(r"\d+", pieces[1]) if 0 <= int(n) - 1 < len(sources)]
    sources_used = []
    if not text.strip().startswith("I could not find this in the documentation.") and not text.strip().startswith("Я не нашёл это в документации"):
        for  n in Sources_used_N:
            sources_used.append(sources[n])
        sources_used = list(set(sources_used))
    return {"answer": pieces[0].strip(),"sources" : sources, "sources_used": sources_used}

if __name__ == "__main__":
    test_questions = [
        # 1.normal questions (answer is in docs)
        "how to declare query parameters",
        "how to enable CORS in FastAPI",
        "how to use dependency injection with Depends",
        "how to return a custom status code",
        "how to upload a file",
        "how to add authentication with OAuth2 and JWT",
        # 2.traps (close topic, no answer in docs)
        "how to use WebSockets with Redis",
        "how to connect FastAPI to MongoDB with Motor",
        "how to deploy FastAPI to AWS Lambda",
        "how to use Celery with FastAPI",
        "how to add rate limiting",
        #3.off-topic (threshold must stop them)
        "how to bake a cake",
        "who won the world cup",
        "what is the capital of France",
        #4. Russian questions
        "как объявить query параметры",
        "как включить CORS",
        #5. edge cases
        "",
        "Depends",
        "how to use query parameters and how to upload a file",
        "how to pass a custom value in request metadata",
    ]

    for q in test_questions:
        res = answer(q)
        print(q)
        print(res["answer"])
        print(res["sources_used"])
        print("-" * 40)