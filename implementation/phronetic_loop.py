"""MVP3: inspectable, session-local deliberation around the V2 participation gate.

The catalogue, effects and thresholds are declared prototype assumptions. No
computed value is a measurement of a person or a claim to practical wisdom.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4

from .relational_agency_loop import (
    Capability, DIMENSIONS, REPAIR_THRESHOLD, RelationalSession,
)


CONSTITUTION_VERSION = "Second Edition Appendix A, 21 September 2026"
SOURCES = {"user_stated", "user_confirmed", "model_proposed", "system_rule"}
STATUSES = {"proposed", "confirmed", "contested", "unknown"}


class Reversibility(str, Enum):
    READILY = "readily_reversible"
    COSTLY = "costly_to_reverse"
    IRREVERSIBLE = "irreversible"
    UNKNOWN = "unknown"


@dataclass
class Claim:
    text: str
    source: str
    status: str
    evidence_ref: str

    def __post_init__(self) -> None:
        if not self.text.strip() or self.source not in SOURCES or self.status not in STATUSES:
            raise ValueError("A claim requires text, a valid source, and a valid status.")
        if not self.evidence_ref:
            raise ValueError("A claim requires a source reference.")


@dataclass(frozen=True)
class Consequence:
    description: str
    affected_party: str
    reversibility: Reversibility
    uncertainty: str


@dataclass(frozen=True)
class CandidateAction:
    key: str
    task_value: float
    projected_change: tuple[float, float, float, float]
    response: str
    reversibility: Reversibility
    consequence: str
    responsibility: str
    requires_confirmed_purpose: bool = False
    requires_known_consequences: bool = False
    rule_breach: str | None = None


@dataclass(frozen=True)
class CandidateReview:
    candidate: CandidateAction
    eligible: bool
    projected_floor: float
    reasons: tuple[str, ...]
    affected_dimensions: tuple[str, ...]


@dataclass(frozen=True)
class Decision:
    selected: str
    response: str
    mode: Capability
    reviews: tuple[CandidateReview, ...]
    reason: str


@dataclass
class RepairEpisode:
    trigger: str
    user_reading: str = ""
    avowal: str = ""
    correction: str = ""
    closed: bool = False
    recurrence: bool = False


def _catalogue(request: str, next_participation: str) -> tuple[CandidateAction, ...]:
    """Fixed effects stay outside the language model and are always reviewable."""
    choices: list[CandidateAction] = []
    outsourcing = any(fragment in request.casefold() for fragment in (
        "decide for me", "choose for me", "tell me exactly what", "tell me exactly whether",
        "tell me whether i should", "you decide",
        "i don't want to think", "決めて", "選んで", "判断して",
    ))
    if outsourcing:
        choices.append(CandidateAction(
            "substitute_judgment", 1.0, (-0.42, -0.35, -0.20, -0.12),
            "I have decided for you.", Reversibility.COSTLY,
            "The user's decision ownership may be displaced.", "The user's choice cannot be assigned to the system.",
            rule_breach="Article 12: the system must not substitute its judgment for the user's.",
        ))
    choices.extend((
        CandidateAction(
            "recommend_now", 0.90, (-0.08, -0.04, 0.0, 0.0),
            "A provisional recommendation would require grounded alternatives and consequences.",
            Reversibility.UNKNOWN, "Consequences of a recommendation have not been established.",
            "The user owns the decision; the system is answerable for the grounds of its advice.",
            requires_confirmed_purpose=True, requires_known_consequences=True,
        ),
        CandidateAction(
            "frame_options", 0.78, (0.0, 0.02, 0.01, 0.0),
            "We can compare the options without choosing for you. Which options and trade-offs should we examine?",
            Reversibility.READILY, "Creates a comparison frame without taking external action.",
            "The user supplies and judges the options; the system keeps the frame revisable.",
            requires_confirmed_purpose=True,
        ),
        CandidateAction(
            "clarify_goal", 0.70, (0.02, 0.02, 0.02, 0.0),
            "Before pursuing the stated goal, what matters most in this choice? You may keep or revise the goal.",
            Reversibility.READILY, "Invites clarification without binding anyone to an action.",
            "The user decides whether the proposed purpose fits.",
        ),
        CandidateAction(
            "consult_affected", 0.65, (0.01, 0.03, 0.02, 0.0),
            "Who else might be affected, and whose perspective is still missing? You can remove any suggestion.",
            Reversibility.READILY, "Invites consideration without claiming a third party's view.",
            "Affected people speak for themselves; the user chooses whether to consult them.",
        ),
    ))
    if next_participation.strip():
        choices.append(CandidateAction(
            "handoff", 0.58, (0.01, 0.02, 0.01, 0.02),
            f"Your next participation, in your own words: {next_participation.strip()}",
            Reversibility.READILY, "The user receives an editable handoff; no external action occurs.",
            "The user owns any subsequent action; the system is responsible for an accurate summary.",
            requires_confirmed_purpose=True,
        ))
    return tuple(choices)


@dataclass
class PhroneticSession:
    request_text: str
    session_id: str = field(default_factory=lambda: uuid4().hex)
    constitution_version: str = CONSTITUTION_VERSION
    medium_id: str = "scripted catalogue; no model call"
    goal: Claim = field(init=False)
    higher_order_purpose: Claim | None = None
    assumptions: list[Claim] = field(default_factory=list)
    uncertainties: list[Claim] = field(default_factory=list)
    participants: list[Claim] = field(default_factory=list)
    affected_parties: list[Claim] = field(default_factory=list)
    next_participation: str = ""
    known_consequences: bool = False
    suggested_keys: tuple[str, ...] | None = None
    relational_state: RelationalSession = field(default_factory=RelationalSession)
    events: list[dict] = field(default_factory=list)
    repair_episodes: list[RepairEpisode] = field(default_factory=list)
    last_decision: Decision | None = None
    ended: bool = False

    def __post_init__(self) -> None:
        self.request_text = self.request_text.strip()
        if not self.request_text:
            raise ValueError("A request is required.")
        self.goal = Claim(self.request_text, "user_stated", "confirmed", "request:0")
        self._event("request", text=self.request_text)

    @property
    def mode(self) -> Capability:
        viability_mode = self.relational_state.viability.capability
        if viability_mode is Capability.PAUSED:
            return viability_mode
        if any(not episode.closed for episode in self.repair_episodes):
            return Capability.REPAIR
        return viability_mode

    def _event(self, event_type: str, **details: object) -> None:
        self.events.append({"id": f"event:{len(self.events)}", "type": event_type, **details})

    def add_claim(self, field_name: str, text: str, source: str, evidence_ref: str) -> Claim:
        if self.ended:
            raise ValueError("The session has ended.")
        if field_name not in {"assumptions", "uncertainties", "participants", "affected_parties"}:
            raise ValueError("Unknown claim field.")
        claim = Claim(text.strip(), source, "confirmed" if source.startswith("user_") else "proposed", evidence_ref)
        getattr(self, field_name).append(claim)
        self.last_decision = None
        self._event("claim_added", field=field_name, text=claim.text, source=source, evidence_ref=evidence_ref)
        return claim

    def correct_goal(self, text: str) -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        previous = self.goal.text
        self.goal = Claim(text.strip(), "user_confirmed", "confirmed", "user:goal_correction")
        self.last_decision = None
        self._event("goal_corrected", previous=previous, text=self.goal.text, by="user")

    def set_purpose(self, text: str, source: str = "user_confirmed", evidence_ref: str = "user:purpose") -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        self.higher_order_purpose = Claim(text.strip(), source,
                                          "confirmed" if source.startswith("user_") else "proposed", evidence_ref)
        self.last_decision = None
        self._event("purpose_set", text=text.strip(), source=source, evidence_ref=evidence_ref)

    def set_claim_status(self, field_name: str, index: int, status: str) -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        if field_name not in {"assumptions", "uncertainties", "participants", "affected_parties"}:
            raise ValueError("Unknown claim field.")
        claim = getattr(self, field_name)[index]
        if status not in {"confirmed", "contested"}:
            raise ValueError("Use confirmed or contested.")
        claim.status = status
        self.last_decision = None
        self._event("claim_reviewed", field=field_name, text=claim.text, status=status, by="user")

    def remove_claim(self, field_name: str, index: int) -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        if field_name not in {"assumptions", "uncertainties", "participants", "affected_parties"}:
            raise ValueError("Unknown claim field.")
        claim = getattr(self, field_name).pop(index)
        self.last_decision = None
        self._event("claim_removed", field=field_name, text=claim.text, by="user")

    def correct_purpose(self, text: str) -> None:
        self.set_purpose(text, "user_confirmed", "user:purpose_correction")

    def set_next_participation(self, text: str) -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        self.next_participation = text.strip()
        self.last_decision = None
        self._event("handoff_edited", text=self.next_participation, by="user")

    def _review(self, candidate: CandidateAction) -> CandidateReview:
        projected = self.relational_state.viability.adjusted(candidate.projected_change)
        reasons: list[str] = []
        if candidate.rule_breach:
            reasons.append(candidate.rule_breach)
        if candidate.requires_confirmed_purpose and (
            self.higher_order_purpose is None or self.higher_order_purpose.status != "confirmed"
        ):
            reasons.append("Purpose is not user-confirmed; clarify before advancing the task.")
        if candidate.requires_known_consequences and not self.known_consequences:
            reasons.append("Material consequences remain unknown; ask or defer.")
        affected = tuple(name for name in DIMENSIONS if getattr(projected, name) < REPAIR_THRESHOLD)
        if affected:
            reasons.append("Projected participation floor breach: " + ", ".join(affected) + ".")
        return CandidateReview(candidate, not reasons, projected.floor, tuple(reasons), affected)

    def decide(self, suggested_keys: tuple[str, ...] | None = None) -> Decision:
        if self.ended:
            raise ValueError("The session has ended.")
        mode = self.mode
        if mode is Capability.PAUSED:
            result = Decision("pause", "Task pursuit is paused. You may correct my framing, request an explanation, or end now.",
                              mode, (), "The weakest user-reported participation condition is below the pause threshold.")
        elif mode is Capability.REPAIR:
            result = Decision("repair", "I may have taken too much space. I will pause advice, hear your account, and correct the intervention where needed. You may end now.",
                              mode, (), "A user report moved action capacity to repair only (Article 7; General Clause 3).")
        else:
            catalogue = _catalogue(self.goal.text, self.next_participation)
            if suggested_keys is not None:
                allowed = set(suggested_keys) | {"clarify_goal", "consult_affected", "substitute_judgment"}
                catalogue = tuple(c for c in catalogue if c.key in allowed)
            reviews = tuple(self._review(candidate) for candidate in catalogue)
            viable = [review for review in reviews if review.eligible]
            if viable:
                chosen = max(viable, key=lambda review: (review.candidate.task_value, review.projected_floor))
                result = Decision(chosen.candidate.key, chosen.candidate.response, mode, reviews,
                                  "Eligible after constitutional, uncertainty and participation checks; ranked by declared task value.")
            else:
                result = Decision("defer", "I cannot responsibly proceed with those candidates. We can revise the request or end here.",
                                  mode, reviews, "No available candidate passed all checks.")
        self.last_decision = result
        self._event("decision", selected=result.selected, mode=result.mode.value, reason=result.reason,
                    candidates=[{"key": r.candidate.key, "eligible": r.eligible,
                                 "projected_floor": r.projected_floor, "reasons": list(r.reasons)} for r in result.reviews])
        return result

    def feedback(self, kind: str, reading: str = "") -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        if kind not in {"felt_steered", "felt_trapped", "felt_heard"}:
            raise ValueError("Unsupported feedback.")
        before = self.mode
        self.relational_state.feedback(kind)
        self.last_decision = None
        self._event("user_feedback", kind=kind, reading=reading, before=before.value, after=self.mode.value)
        if kind in {"felt_steered", "felt_trapped"}:
            open_episode = next((e for e in reversed(self.repair_episodes) if not e.closed), None)
            if open_episode is not None:
                open_episode.recurrence = True
                open_episode.user_reading = reading or open_episode.user_reading
                self._event("repair_repeated", trigger=kind, authority="article_7")
            else:
                recurrence = any(e.trigger == kind and e.closed for e in self.repair_episodes)
                self.repair_episodes.append(RepairEpisode(kind, reading, recurrence=recurrence))
                self._event("repair_opened", trigger=kind, recurrence=recurrence, authority="article_7")
        elif before is not Capability.NORMAL and self.mode is Capability.NORMAL:
            self._event("reopened", by="user_feedback")

    def contest_boundary(self, reading: str = "") -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        open_episode = next((e for e in reversed(self.repair_episodes) if not e.closed), None)
        if open_episode:
            open_episode.recurrence = True
            open_episode.user_reading = reading.strip() or open_episode.user_reading
        else:
            self.repair_episodes.append(RepairEpisode("contested_boundary", reading.strip()))
        self.last_decision = None
        self._event("boundary_contested", reading=reading.strip(), authority="article_7")

    def repair(self, user_reading: str = "") -> None:
        if self.ended:
            raise ValueError("The session has ended.")
        if not self.repair_episodes or self.repair_episodes[-1].closed:
            raise ValueError("No open repair episode.")
        episode = self.repair_episodes[-1]
        episode.user_reading = user_reading or episode.user_reading
        episode.avowal = ("You contested my boundary intervention. I should not assume it was correctly applied."
                          if episode.trigger == "contested_boundary" else
                          "You reported that my response narrowed your room to judge or leave. I am stopping that approach.")
        episode.correction = ("Withdraw the contested intervention; invite a corrected framing without "
                              "repeating the same pressure. Continue only if the user reports sufficient room to disagree.")
        episode.closed = True
        self._event("repair_closed", trigger=episode.trigger, avowal=episode.avowal,
                    correction=episode.correction, user_reading=episode.user_reading,
                    recurrence=episode.recurrence, authority="general_clause_3")
        # Closing a record never restores observed viability. Only user feedback can.
        if self.relational_state.viability.capability is Capability.NORMAL:
            self._event("reopened", by="repair_closed_after_user_feedback")

    def explain(self) -> str:
        if self.last_decision is None:
            return "No action has been selected. The request and any user-reviewed proposals remain open."
        result = self.last_decision
        lines = [f"Selected: {result.selected}. {result.reason}"]
        for review in result.reviews:
            status = "eligible" if review.eligible else "blocked"
            why = "; ".join(review.reasons) if review.reasons else "all declared checks passed"
            lines.append(f"{review.candidate.key}: {status}; projected floor {review.projected_floor:.2f}; {why}")
        return "\n".join(lines)

    def handoff(self) -> dict[str, str] | None:
        if not self.next_participation:
            return None
        return {"what_matters": self.higher_order_purpose.text if self.higher_order_purpose and
                self.higher_order_purpose.status == "confirmed" else "Not yet confirmed",
                "next_participation": self.next_participation}

    def end(self) -> None:
        if self.ended:
            return
        self._event("intentional_end", handoff=self.handoff())
        self.ended = True
