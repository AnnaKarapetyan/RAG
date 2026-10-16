from retriever import retrieve
import json

test_questions = [
    {"question": "how to create and run my first fastapi app",
    "expected": ["https://fastapi.tiangolo.com/tutorial/first-steps/"]},
    {"question": "how to get a value from the URL path",
     "expected": ["https://fastapi.tiangolo.com/tutorial/path-params/"]},
    {"question": "how to receive JSON data in a POST request",
     "expected": ["https://fastapi.tiangolo.com/tutorial/body/"]},
    {"question": "how to return an error with a 404 status code",
     "expected": ["https://fastapi.tiangolo.com/tutorial/handling-errors/"]},
    {"question": "how to allow requests from another domain in the browser",
     "expected": ["https://fastapi.tiangolo.com/tutorial/cors/"]},
    {"question": "how to let users upload a file",
     "expected": ["https://fastapi.tiangolo.com/tutorial/request-files/"]},
    {"question": "how to run a task after sending the response",
     "expected": ["https://fastapi.tiangolo.com/tutorial/background-tasks/"]},
    {"question": "how to hide a field like password from the response",
     "expected": ["https://fastapi.tiangolo.com/tutorial/response-model/"]},
    {"question": "how to split a big app into several files",
     "expected": ["https://fastapi.tiangolo.com/tutorial/bigger-applications/"]},
    {"question": "how to run code for every request before it reaches the endpoint",
     "expected": ["https://fastapi.tiangolo.com/tutorial/middleware/"]},
    {"question": "how can I make sure a user is logged in before my endpoint runs",
     "expected": ["https://fastapi.tiangolo.com/tutorial/security/get-current-user/",
                  "https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/",
                  "https://fastapi.tiangolo.com/tutorial/dependencies/"]},
    {"question": "how to read values sent after the question mark in the address",
     "expected": ["https://fastapi.tiangolo.com/tutorial/query-params/"]},
    {"question": "how to give different permissions to different users",
     "expected": ["https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/"]},
    {"question": "how to reuse the same logic in many endpoints",
     "expected": ["https://fastapi.tiangolo.com/tutorial/dependencies/",
                  "https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/"]},
    {"question": "how to read a custom value that the client sends in the request metadata",
     "expected": ["https://fastapi.tiangolo.com/tutorial/header-params/"]},
]
urls = [
    "https://fastapi.tiangolo.com/tutorial/first-steps/",
    "https://fastapi.tiangolo.com/tutorial/path-params/",
    "https://fastapi.tiangolo.com/tutorial/body/",
    "https://fastapi.tiangolo.com/tutorial/handling-errors/",
    "https://fastapi.tiangolo.com/tutorial/cors/",
    "https://fastapi.tiangolo.com/tutorial/request-files/",
    "https://fastapi.tiangolo.com/tutorial/background-tasks/",
    "https://fastapi.tiangolo.com/tutorial/response-model/",
    "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    "https://fastapi.tiangolo.com/tutorial/middleware/",
    "https://fastapi.tiangolo.com/tutorial/security/get-current-user/",
    "https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/",
    "https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/",
    "https://fastapi.tiangolo.com/tutorial/query-params/",
    "https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/",
    "https://fastapi.tiangolo.com/tutorial/header-params/",
]
fake_questions = ["how to bake a cake", "who won the world cup"]

all_urls = set()
with open("chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        all_urls.add(json.loads(line)["url"])

for u in urls:
    print(u in all_urls, u)
from retriever import retrieve

def evaluate(k):
    presents = 0
    miss = []
    max_dist = 0

    for question in test_questions:
        results = retrieve(question["question"], k)
        found_urls = [r["url"]  for r in results]
        if any(u in found_urls for u in question["expected"]):
            presents += 1
        else:
            miss.append(question["question"])
    return presents / len(test_questions), miss

for k in [3, 5, 8]:
    rate, misses = evaluate(k)
    print(f"k={k}: rate = {rate*100}%")
    print("bad answers", misses)

for q in fake_questions:
    results = retrieve(q, 3)
    print(q, [round(r["distance"], 3) for r in results])

distances = []
for question in test_questions:
    top = retrieve(question["question"], 1)[0]
    d = top["distance"]
    distances.append(d)

print("max:", max(distances))