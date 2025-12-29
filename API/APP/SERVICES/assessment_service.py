from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from APP.MODELS.question import Question
from APP.REPOSITORIES.question_repository import QuestionRepository


@dataclass  # using dataclass for simplicity
class QuestionInput:  # structure to hold question input data
    id: int
    weight: float
    dimension: str | None
    is_inverted: bool
    answer_value: int  # 0...4


def _invert_value(value: int) -> int:
    """Inverts the answer value for inverted questions."""

    return 4 - value


def calculate_assessment(
    question_inputs: List[QuestionInput],
    risk_thresholds: Tuple[float, float, float, float] = (25, 50, 70, 85),
) -> Dict[str, Any]:
    """Returns a dictionary with:
    - score_total, score_max, percent, risk_level
    - per_dimension breakdown
    -per-question breakdown
    """

    question_breakdown: List[Dict[str, Any]] = []
    total_score = 0.0
    total_max = 0.0

    # per-dimension accumulators
    dim_acc = {}

    # Process each question input
    for qi in question_inputs:
        val = qi.answer_value
        inverted = False
        if qi.is_inverted:  # invert value if question is inverted
            val = _invert_value(val)
            inverted = True

        q_score = qi.weight * val
        q_max = qi.weight * 4  # max value per question is 4

        total_score += q_score
        total_max += q_max

        # accumulate by dimension
        dim = qi.dimension or "outros"
        if dim not in dim_acc:
            dim_acc[dim] = {"score": 0.0, "max": 0.0}
        dim_acc[dim]["score"] += q_score  # accumulate score for dimension
        dim_acc[dim]["max"] += q_max  # accumulate maximum possible score

        question_breakdown.append(
            {
                "question_id": qi.id,
                "weight": qi.weight,
                "value_used": qi.answer_value,
                "inverted": inverted,
                "score": round(q_score, 2),
                "dimension": qi.dimension,
            }
        )

    # Calculate percentage
    percent = (total_score / total_max * 100) if total_max > 0 else 0.0
    percent_rounded = round(percent, 2)

    # Determine risk level based on thresholds (percentages)
    t25, t50, t70, t85 = risk_thresholds
    if percent_rounded < t25:
        risk = "Sem risco"
    elif percent_rounded < t50:
        risk = "Risco leve"
    elif percent_rounded < t70:
        risk = "Risco moderado"
    elif percent_rounded < t85:
        risk = "Risco elevado"
    else:
        risk = "Risco crítico"

    # per-dimension percent
    per_dimension: Dict[Any, Any] = {}
    for dim, acc in dim_acc.items():
        dim_percent = (acc["score"] / acc["max"] * 100) if acc["max"] > 0 else 0.0
        per_dimension[dim] = {
            "score": round(acc["score"], 2),
            "max": round(acc["max"], 2),
            "percent": round(dim_percent, 2),
        }

    result: Dict[str, Any] = {
        "score_total": round(total_score, 2),
        "score_max": round(total_max, 2),
        "score_percent": percent_rounded,
        "risk_level": risk,
        "per_dimension": per_dimension,
        "question_breakdown": question_breakdown,
    }
    return result


def build_question_inputs(
    responses: List[Dict[Any, Any]], question_repo: QuestionRepository
) -> List[QuestionInput]:
    """Builds a list of questions"""

    qids = [resp["question_id"] for resp in responses]
    qmap: Dict[int, Question] = question_repo.get_question_map(qids)

    q_inputs: List[QuestionInput] = []

    for resp in responses:
        q = qmap.get(resp["question_id"])
        if not q:
            continue

        q_inputs.append(
            QuestionInput(
                id=q.question_id,
                weight=float(q.weight),
                dimension=q.dimension,
                is_inverted=bool(q.is_inverted),
                answer_value=int(resp["answer_value"]),
            )
        )
    return q_inputs
