import requests
import json
import time
import os

BASE_URL = "http://localhost:8000/api/ask"
JSON_PATH = r"C:\Users\kesav\OneDrive\Documents\Python Q&A Assistant\python-qa-assistant\scratch\evaluation_raw_results.json"

if not os.path.exists(JSON_PATH):
    print("Results file not found.")
    exit(1)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

retry_queries = {
    "Q1": "How do I read a CSV file using pandas?",
    "Q6": "How do I filter a list using list comprehensions with conditions?",
    "Q8": "What is the GIL in Python and how does it affect multithreading?"
}

def execute_retry(q_id, question):
    print(f"Retrying {q_id}: '{question}'")
    for attempt in range(1, 4):
        t0 = time.time()
        try:
            print(f"  Attempt {attempt}/3...")
            r = requests.post(BASE_URL, json={"question": question, "chat_history": []}, timeout=150)
            elapsed_ms = int((time.time() - t0) * 1000)
            
            if r.status_code == 200:
                res_dict = r.json()
                is_off_topic = "fallback" in res_dict.get("steps_taken", [])
                
                # Check PASS/FAIL criteria
                answer = res_dict.get("answer", "")
                sources = res_dict.get("sources", [])
                
                passed = False
                if answer and len(sources) > 0 and not is_off_topic and len(answer) > 50:
                    passed = True
                    
                status = "PASS" if passed else "FAIL"
                
                results[q_id] = {
                    "question": question,
                    "status_code": r.status_code,
                    "elapsed_ms": elapsed_ms,
                    "response": res_dict,
                    "is_off_topic": is_off_topic,
                    "status": status
                }
                print(f"  [✓] Success on attempt {attempt}! Finished in {elapsed_ms} ms. Status: {status}")
                return True
            else:
                print(f"  [x] Attempt {attempt} returned status {r.status_code}")
                time.sleep(2)
        except Exception as e:
            elapsed_ms = int((time.time() - t0) * 1000)
            print(f"  [x] Attempt {attempt} failed: {e}")
            time.sleep(2)
            
    print(f"  [!] All attempts failed for {q_id}")
    return False

updated = False
for q_id, q in retry_queries.items():
    if q_id in results and results[q_id].get("status") == "FAIL" and "timeout" in results[q_id].get("error", "").lower():
        if execute_retry(q_id, q):
            updated = True
        time.sleep(2)

if updated:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Updated results file successfully!")
else:
    print("No updates made.")
