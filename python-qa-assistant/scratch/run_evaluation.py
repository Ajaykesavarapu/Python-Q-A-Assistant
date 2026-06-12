import requests
import json
import time
import os

BASE_URL = "http://localhost:8000/api/ask"

queries = [
    ("Q1", "How do I read a CSV file using pandas?"),
    ("Q2", "What is the difference between a list and a tuple in Python?"),
    ("Q3", "How do I handle exceptions in Python with try/except?"),
    ("Q4", "How to merge two dictionaries in Python 3?"),
    ("Q5", "What is a lambda function and when should I use it?"),
    ("Q6", "How do I filter a list using list comprehensions with conditions?"),
    ("Q7", "How to connect to a SQLite database and execute queries in Python?"),
    ("Q8", "What is the GIL in Python and how does it affect multithreading?")
]

edge_cases = [
    ("E1", ""),
    ("E2", "What is the capital of France?"),
    ("E3", "xyzqwertyabcdef1234 python")
]

all_results = {}

def execute_request(q_id, question):
    print(f"Executing {q_id}: '{question}'")
    t0 = time.time()
    try:
        if question == "":
            # FastAPI returns 422 validation error
            r = requests.post(BASE_URL, json={"question": question, "chat_history": []}, timeout=150)
        else:
            r = requests.post(BASE_URL, json={"question": question, "chat_history": []}, timeout=150)
            
        elapsed_ms = int((time.time() - t0) * 1000)
        
        if r.status_code == 200:
            res_dict = r.json()
            # The schema doesn't have is_off_topic, but we can compute/derive it based on steps_taken
            is_off_topic = "fallback" in res_dict.get("steps_taken", [])
            
            # Check PASS/FAIL criteria
            # PASS if answer is not null AND sources not empty AND is_off_topic is false AND answer length > 50 chars
            answer = res_dict.get("answer", "")
            sources = res_dict.get("sources", [])
            
            passed = False
            if answer and len(sources) > 0 and not is_off_topic and len(answer) > 50:
                passed = True
                
            status = "PASS" if passed else "FAIL"
            
            all_results[q_id] = {
                "question": question,
                "status_code": r.status_code,
                "elapsed_ms": elapsed_ms,
                "response": res_dict,
                "is_off_topic": is_off_topic,
                "status": status
            }
        else:
            try:
                err_detail = r.json()
            except:
                err_detail = r.text
            all_results[q_id] = {
                "question": question,
                "status_code": r.status_code,
                "elapsed_ms": elapsed_ms,
                "error": err_detail,
                "is_off_topic": True if q_id == "E2" else False,
                "status": "FAIL"
            }
    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        print(f"Error executing {q_id}: {e}")
        all_results[q_id] = {
            "question": question,
            "status_code": 500,
            "elapsed_ms": elapsed_ms,
            "error": str(e),
            "is_off_topic": False,
            "status": "FAIL"
        }
    print(f"Finished {q_id} in {elapsed_ms} ms with status {all_results[q_id].get('status')}")

# Run queries
for q_id, q in queries:
    execute_request(q_id, q)
    time.sleep(1)

# Run edge cases
for q_id, q in edge_cases:
    execute_request(q_id, q)
    time.sleep(1)

# Save results to json file
out_path = r"C:\Users\kesav\OneDrive\Documents\Python Q&A Assistant\python-qa-assistant\scratch\evaluation_raw_results.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2)
print(f"Saved results to {out_path}")
