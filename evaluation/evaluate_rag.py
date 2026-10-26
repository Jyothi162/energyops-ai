
import json
import sys
from pathlib import Path

# Main EnergyOps AI project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allow importing modules from the project root
sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import retrieve_documents

EVALUATION_DIR = Path(__file__).resolve().parent
TEST_CASES_FILE = EVALUATION_DIR / "rag_test_cases.json"
RESULTS_FILE = EVALUATION_DIR / "rag_results.json"

TOP_K = 2


def evaluate_rag():
    with open(TEST_CASES_FILE, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    total = len(test_cases)
    correct = 0
    completed = 0
    results = []

    print("\n===== ENERGYOPS AI RAG EVALUATION =====\n")

    for case in test_cases:
        print(f"Test {case['id']}: {case['question']}")

        try:
            documents = retrieve_documents(
                question=case["question"],
                top_k=TOP_K
            )

            retrieved_sources = [
                Path(doc["source"]).name
                for doc in documents
            ]

            expected_source = Path(
                case["expected_source"]
            ).name

            matched = expected_source in retrieved_sources

            correct += int(matched)
            completed += 1

            results.append({
                "id": case["id"],
                "question": case["question"],
                "expected_source": expected_source,
                "retrieved_sources": retrieved_sources,
                "passed": matched,
                "error": None
            })

            print(f"  Expected: {expected_source}")
            print(f"  Retrieved: {retrieved_sources}")
            print(f"  Result: {'PASS' if matched else 'FAIL'}")

        except Exception as error:
            results.append({
                "id": case["id"],
                "question": case["question"],
                "expected_source": case["expected_source"],
                "retrieved_sources": [],
                "passed": False,
                "error": str(error)
            })

            print(f"  ERROR: {error}")

        print()

    recall_at_k = (
        correct / total * 100 if total else 0
    )

    summary = {
        "metric": f"Source Hit Rate@{TOP_K}",
        "total_cases": total,
        "completed_cases": completed,
        "correct_cases": correct,
        "source_hit_rate_percent": round(recall_at_k, 2),
        "results": results
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("===== RAG EVALUATION SUMMARY =====")
    print(f"Total cases:       {total}")
    print(f"Completed cases:   {completed}")
    print(f"Correct cases:     {correct}")
    print(f"Source Hit Rate@{TOP_K}: {recall_at_k:.2f}%")
    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    evaluate_rag()
