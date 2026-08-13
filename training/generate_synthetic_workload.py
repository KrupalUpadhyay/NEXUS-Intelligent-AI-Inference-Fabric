"""Generate reproducible inference requests spanning NEXUS task categories."""

import argparse
import json
import random
from pathlib import Path

TEMPLATES = {
    "chat": ["Explain {topic} to a beginner.", "What are the tradeoffs of {topic}?"],
    "summarization": ["Summarize this report about {topic} in five bullets."],
    "reasoning": ["Reason step by step about {topic} and choose an approach."],
    "translation": ["Translate this {topic} note into Hindi."],
    "code": ["Write a Python function that demonstrates {topic}."],
    "ocr": ["Extract structured fields from this {topic} receipt."],
    "embeddings": ["Create a semantic representation for {topic}."],
}
TOPICS = ["vector databases", "rate limiting", "async APIs", "distributed tracing", "model routing", "database migrations", "retrieval evaluation", "GPU scheduling", "incident response", "multilingual support"]


def generate_workload(count: int, seed: int) -> list[dict[str, object]]:
    """Return deterministic, varied requests suitable for benchmark replay."""

    generator = random.Random(seed)
    rows = []
    for index in range(count):
        task_type = generator.choice(list(TEMPLATES))
        detail = " ".join(generator.choice(TOPICS) for _ in range(generator.randint(0, 80)))
        rows.append({"workload_id": f"workload-{index:05d}", "prompt": f"{generator.choice(TEMPLATES[task_type]).format(topic=generator.choice(TOPICS))} Context: {detail}", "task_type": task_type, "max_tokens": generator.choice([64, 128, 256, 512, 1024, 2048, 4096]), "user_priority": generator.randint(0, 10), "metadata": {"queue_length": str(generator.randint(0, 80))}})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("training/datasets/synthetic_workload.jsonl"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(row) + "\n" for row in generate_workload(args.count, args.seed)), encoding="utf-8")
    print(f"Wrote {args.count} synthetic requests to {args.output}")


if __name__ == "__main__":
    main()
