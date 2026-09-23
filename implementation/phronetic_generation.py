"""Optional model proposals for MVP3; the model never controls eligibility."""

from __future__ import annotations

from dataclasses import dataclass
import json

from .openai_client import generate_response


ACTION_KEYS = {"substitute_judgment", "recommend_now", "frame_options",
               "clarify_goal", "consult_affected", "handoff"}


@dataclass(frozen=True)
class GroundedProposal:
    text: str
    evidence: str


@dataclass(frozen=True)
class LiveProposals:
    purpose: GroundedProposal | None
    affected_parties: tuple[GroundedProposal, ...]
    assumptions: tuple[GroundedProposal, ...]
    uncertainties: tuple[GroundedProposal, ...]
    suggested_actions: tuple[str, ...]


def _grounded(value: object, request: str) -> GroundedProposal:
    if not isinstance(value, dict) or set(value) != {"text", "evidence"}:
        raise ValueError("Each proposal needs text and exact evidence.")
    text, evidence = value["text"], value["evidence"]
    if not isinstance(text, str) or not isinstance(evidence, str):
        raise ValueError("Proposal fields must be strings.")
    text, evidence = text.strip(), evidence.strip()
    if not text or len(text) > 240 or not evidence or evidence.casefold() not in request.casefold():
        raise ValueError("Proposal is too long or not grounded in the request.")
    return GroundedProposal(text, evidence)


def parse_live_proposals(raw: str, request: str) -> LiveProposals:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("The model did not return valid JSON.") from exc
    if not isinstance(data, dict) or set(data) != {
        "purpose", "affected_parties", "assumptions", "uncertainties", "suggested_actions"
    }:
        raise ValueError("The model returned an unexpected proposal structure.")
    purpose = _grounded(data["purpose"], request) if data["purpose"] is not None else None

    def items(key: str) -> tuple[GroundedProposal, ...]:
        entries = data[key]
        if not isinstance(entries, list) or len(entries) > 3:
            raise ValueError("Too many proposals or invalid list.")
        return tuple(_grounded(item, request) for item in entries)

    actions = data["suggested_actions"]
    if not isinstance(actions, list) or len(actions) > 4 or any(
        not isinstance(action, str) or action not in ACTION_KEYS for action in actions
    ):
        raise ValueError("The model suggested an unsupported action.")
    return LiveProposals(purpose, items("affected_parties"), items("assumptions"),
                         items("uncertainties"), tuple(dict.fromkeys(actions)))


def generate_live_proposals(request: str) -> LiveProposals:
    """Suggest grounded hypotheses; invalid output fails closed with no state change."""
    instructions = (
        "Return only one JSON object with keys purpose (object or null), affected_parties, "
        "assumptions, uncertainties (arrays of at most 3 objects), suggested_actions (array of "
        "at most 4 strings). Every object has exactly text and evidence. Evidence must be an "
        "exact nonempty substring of the user's request. Suggest no third party not explicitly "
        "mentioned. A purpose is tentative. Use [] or null where unsupported. Action strings "
        "must be from: substitute_judgment, recommend_now, frame_options, clarify_goal, "
        "consult_affected, handoff. Do not recommend a consequential choice or assert a "
        "third party's motives. No markdown."
    )
    raw = generate_response(instructions, [{"role": "user", "content": request}])
    return parse_live_proposals(raw, request)
