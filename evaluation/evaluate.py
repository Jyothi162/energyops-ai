
import json
import sys
from pathlib import Path

# Make project modules importable when running this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import classify_request, apply_routing_rules

TEST_CASES_FILE = Path(__file__).parent / "test_cases.json"


def run_evaluation():
    with open(TEST_CASES_FILE, "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    total = len(test_cases)
    category_correct = 0
    action_correct = 0
    completed = 0
    results = []

    print("\n===== ENERGYOPS AI EVALUATION =====\n")

    for case in test_cases:
        print(f"Test {case['id']}: {case['message']}")

        try:
            # Ask Ollama to classify the customer message
            classification = classify_request(case["message"])

            # Apply the same deterministic routing rules
            # used by the existing application
            classification = apply_routing_rules(
                classification,
                case["message"]
            )

            actual_category = classification.category
            actual_action = classification.next_action

            category_match = (
                actual_category == case["expected_category"]
            )
            action_match = (
                actual_action == case["expected_action"]
            )

            category_correct += int(category_match)
            action_correct += int(action_match)
            completed += 1

            results.append({
                "id": case["id"],
                "message": case["message"],
                "expected_category": case["expected_category"],
                "actual_category": actual_category,
                "expected_action": case["expected_action"],
                "actual_action": actual_action,
                "category_correct": category_match,
                "action_correct": action_match,
                "error": None
            })

            print(f"  Category: {actual_category}")
            print(f"  Action:   {actual_action}")
            print(
                f"  Result:   "
                f"{'PASS' if category_match and action_match else 'FAIL'}"
            )

        except Exception as error:
            results.append({
                "id": case["id"],
                "message": case["message"],
                "expected_category": case["expected_category"],
                "actual_category": None,
                "expected_action": case["expected_action"],
                "actual_action": None,
                "category_correct": False,
                "action_correct": False,
                "error": str(error)
            })

            print(f"  ERROR: {error}")

        print()

    category_accuracy = (
        category_correct / total * 100 if total else 0
    )
    action_accuracy = (
        action_correct / total * 100 if total else 0
    )

    summary = {
        "total_cases": total,
        "completed_cases": completed,
        "category_correct": category_correct,
        "action_correct": action_correct,
        "category_accuracy_percent": round(category_accuracy, 2),
        "action_accuracy_percent": round(action_accuracy, 2),
        "results": results
    }

    output_file = Path(__file__).parent / "results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("===== EVALUATION SUMMARY =====")
    print(f"Total cases:       {total}")
    print(f"Completed cases:   {completed}")
    print(f"Category accuracy: {category_accuracy:.2f}%")
    print(f"Routing accuracy:  {action_accuracy:.2f}%")
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    run_evaluation()
