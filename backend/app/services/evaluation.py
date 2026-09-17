"""
Evaluation service — backs the Evaluation tab.

Runs a batch of test questions through the existing /ask pipeline
(answer_question — the same retrieval + generation used by Chat) and
checks whether each expected source file actually turned up in the
sources the pipeline retrieved. This measures *retrieval* quality
directly: if the right file never surfaces in `sources`, the LLM had
no chance of grounding its answer in it, regardless of how the answer
reads.
"""

from __future__ import annotations

import time

from app.models.schemas import EvalQuestionResult, EvalRequest, EvalResponse
from app.services.qa import answer_question


def _is_correct(expected_source: str, retrieved_sources: list[str]) -> bool:
    return any(expected_source in path for path in retrieved_sources)


def run_evaluation(repo_id: str, request: EvalRequest) -> EvalResponse:
    results: list[EvalQuestionResult] = []

    for item in request.questions:
        start = time.monotonic()
        response = answer_question(repo_id, item.question)
        elapsed_ms = (time.monotonic() - start) * 1000

        retrieved_sources = [source.file_path for source in response.sources]
        results.append(
            EvalQuestionResult(
                question=item.question,
                expected_source=item.expected_source,
                retrieved_sources=retrieved_sources,
                correct=_is_correct(item.expected_source, retrieved_sources),
                response_time_ms=round(elapsed_ms),
            )
        )

    total = len(results)
    correct_count = sum(1 for r in results if r.correct)
    accuracy_percent = round((correct_count / total) * 100, 1) if total else 0.0
    avg_response_time_ms = round(sum(r.response_time_ms for r in results) / total, 1) if total else 0.0

    return EvalResponse(
        repo_id=repo_id,
        results=results,
        total_questions=total,
        accuracy_percent=accuracy_percent,
        avg_response_time_ms=avg_response_time_ms,
    )
