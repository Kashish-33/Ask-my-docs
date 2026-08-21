import requests
import json
import time

API_URL = "http://localhost:8000"

queries = [
    "What is the main problem this project addresses?",
    "What are the three key problems with centralized data collection?",
    "What does Federated Learning allow hospitals to do?",
    "What is the limitation of Federated Learning alone, without differential privacy?",
    "What are the primary objectives of this project?",
    "What are the secondary objectives of this project?",
    "What technologies are used for the Federated Learning component?",
    "What are the steps in the differential privacy pipeline?",
    "What evaluation metrics will be used to measure performance?",
    "What is the difference between centralized ML, Federated Learning, and FL+DP in terms of privacy?",
    "What accuracy did the model achieve?",
    "What is the exact name of the dataset used?",
    "What epsilon value was used for differential privacy?",
    "How many hospitals participated in the actual experiment?",
    "What was the final loss value after training?",
    "How long did the full training process take?",
    "Who are the authors of this project?",
    "What programming language version was used?",
    "What was the F1-score achieved on the test set?",
    "Which specific medical condition/disease was diagnosed by the model?",
]

results = []

for i, q in enumerate(queries):
    print(f"[{i+1}/{len(queries)}] Asking: {q}")
    response = requests.post(f"{API_URL}/ask", json={"question": q}, timeout=60)
    data = response.json()
    results.append({
        "query": q,
        "answer": data.get("answer"),
        "confidence": data.get("confidence_score"),
        "retries": data.get("retries_used")
    })
    time.sleep(1)  # avoid rate limits

with open("evaluation_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n=== SUMMARY ===")
high_conf = sum(1 for r in results if r["confidence"] and r["confidence"] >= 4)
retried = sum(1 for r in results if r["retries"] and r["retries"] > 0)
avg_conf = sum(r["confidence"] for r in results if r["confidence"]) / len(results)

print(f"Total queries: {len(results)}")
print(f"High confidence (>=4): {high_conf}/{len(results)} ({high_conf/len(results)*100:.1f}%)")
print(f"Required retry: {retried}/{len(results)} ({retried/len(results)*100:.1f}%)")
print(f"Average confidence score: {avg_conf:.2f}/5")