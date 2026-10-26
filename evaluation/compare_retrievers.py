
import json
import sys
from pathlib import Path

# Allow imports from the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from rag.retriever import retrieve_documents
from rag.hybrid_retriever import hybrid_retrieve


TEST_CASES = [
    {
        "question": "Why is the amount on my solar power statement higher than expected?",
        "expected": "billing_faq.txt",
    },
    {
        "question": "How do I get help with a payment discrepancy?",
        "expected": "billing_faq.txt",
    },
    {
        "question": "What should I do if my inverter keeps shutting down?",
        "expected": "inverter_troubleshooting.txt",
    },
    {
        "question": "How can I check whether my solar panel installation is delayed?",
        "expected": "installation_guide.txt",
    },
    {
        "question": "Who should I contact if my solar equipment shows an error code?",
        "expected": "inverter_troubleshooting.txt",
    },
]


def evaluate_retriever(name, retrieval_function):
    results = []
    hit_count = 0
    reciprocal_rank_total = 0.0

    print(f"\n===== {name.upper()} RETRIEVAL =====")

    for case in TEST_CASES:
        question = case["question"]
        expected = case["expected"]

        try:
            documents = retrieval_function(question, top_k=3)

            retrieved = [
                document["source"]
                for document in documents
            ]

            hit = expected in retrieved[:2]

            rank = (
                retrieved.index(expected) + 1
                if expected in retrieved
                else None
            )

            reciprocal_rank = (
                1 / rank if rank is not None else 0.0
            )

            hit_count += int(hit)
            reciprocal_rank_total += reciprocal_rank

            results.append({
                "question": question,
                "expected": expected,
                "retrieved": retrieved,
                "hit_at_2": hit,
                "rank": rank,
                "reciprocal_rank": reciprocal_rank,
            })

            print(f"\nQuestion: {question}")
            print(f"Expected: {expected}")
            print(f"Retrieved: {retrieved}")
            print(f"Hit@2: {hit}")
            print(f"Rank: {rank}")

        except Exception as error:
            print(f"\nERROR: {question}")
            print(error)

            results.append({
                "question": question,
                "expected": expected,
                "error": str(error),
            })

    total = len(TEST_CASES)

    return {
        "method": name,
        "total_cases": total,
        "completed_cases": sum(
            "error" not in result for result in results
        ),
        "hit_rate_at_2": hit_count / total,
        "mrr": reciprocal_rank_total / total,
        "results": results,
    }


def main():
    semantic = evaluate_retriever(
        "Semantic",
        retrieve_documents
    )

    hybrid = evaluate_retriever(
        "Hybrid",
        hybrid_retrieve
    )

    report = {
        "semantic": semantic,
        "hybrid": hybrid,
    }

    output_path = (
        BASE_DIR / "evaluation" / "comparison_results.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n===== REAL RETRIEVAL COMPARISON =====")

    for result in [semantic, hybrid]:
        print(
            f"{result['method']}: "
            f"Hit@2={result['hit_rate_at_2']:.1%}, "
            f"MRR={result['mrr']:.3f}, "
            f"Completed={result['completed_cases']}/"
            f"{result['total_cases']}"
        )

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
