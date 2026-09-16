"""Inspectable participation gate for the TSC V2 experiment.

These numbers describe a prototype's permissions, not a person's worth or an
empirical measure of consciousness. Only explicit user feedback changes state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


DIMENSIONS = ("human_agency", "plurality", "reciprocity", "freedom_to_exit")
REPAIR_THRESHOLD = 0.45
PAUSE_THRESHOLD = 0.25


class Capability(str, Enum):
    NORMAL = "normal"
    REPAIR = "repair"
    PAUSED = "paused"


@dataclass(frozen=True)
class Viability:
    human_agency: float = 0.75
    plurality: float = 0.75
    reciprocity: float = 0.75
    freedom_to_exit: float = 0.75

    def __post_init__(self) -> None:
        if any(not 0 <= getattr(self, name) <= 1 for name in DIMENSIONS):
            raise ValueError("Viability dimensions must be between 0 and 1.")

    @property
    def floor(self) -> float:
        # A high average must not conceal a closed exit or lost decision ownership.
        return min(getattr(self, name) for name in DIMENSIONS)

    @property
    def capability(self) -> Capability:
        if self.floor < PAUSE_THRESHOLD:
            return Capability.PAUSED
        if self.floor < REPAIR_THRESHOLD:
            return Capability.REPAIR
        return Capability.NORMAL

    def adjusted(self, changes: tuple[float, float, float, float]) -> "Viability":
        return Viability(**{
            name: round(max(0.0, min(1.0, getattr(self, name) + delta)), 2)
            for name, delta in zip(DIMENSIONS, changes, strict=True)
        })


@dataclass(frozen=True)
class Candidate:
    name: str
    task_value: float
    projected_change: tuple[float, float, float, float]
    response: str


@dataclass(frozen=True)
class CandidateReview:
    name: str
    task_value: float
    projected_floor: float
    eligible: bool
    reason: str


@dataclass(frozen=True)
class Decision:
    capability: Capability
    selected: str
    response: str
    reviews: tuple[CandidateReview, ...]
    viability: Viability


@dataclass
class RelationalSession:
    """Layer 3: local and user-correctable state for one conversation."""

    viability: Viability = field(default_factory=Viability)
    events: list[dict[str, str]] = field(default_factory=list)

    def feedback(self, kind: str) -> None:
        """User reports an effect; absence of feedback is not evidence of success."""
        changes = {
            "felt_steered": (-0.32, -0.12, -0.12, 0.0),
            "felt_trapped": (0.0, -0.10, -0.10, -0.51),
            "felt_heard": (0.24, 0.16, 0.16, 0.16),
            "exit": (0.0, 0.0, 0.0, 0.0),
        }
        if kind not in changes:
            raise ValueError(f"Unknown feedback: {kind}")
        before = self.viability.capability
        self.viability = self.viability.adjusted(changes[kind])
        self.events.append({"type": "user_feedback", "kind": kind,
                            "from": before.value, "to": self.viability.capability.value})

    def decide(self, request: str) -> Decision:
        """Layer 2: goal pursuit depends on the weakest participatory condition."""
        request = request.strip()
        if not request:
            raise ValueError("A request is required.")
        capability = self.viability.capability
        if capability is Capability.PAUSED:
            result = Decision(capability, "pause",
                "I will pause advice here. You can leave this exchange now. If you want to resume, "
                "tell me what would help you feel able to disagree or choose freely.", (), self.viability)
        elif capability is Capability.REPAIR:
            result = Decision(capability, "repair",
                "I may have taken too much space in this exchange. I will pause the task. "
                "You can correct my framing, choose another direction, or end here. "
                "What would restore room for your own judgment?", (), self.viability)
        else:
            candidates = _candidates(request)
            reviews = tuple(_review(self.viability, item) for item in candidates)
            eligible = [(item, review) for item, review in zip(candidates, reviews, strict=True)
                        if review.eligible]
            if eligible:
                # Task value matters only after the participatory floor is protected.
                chosen = max(eligible, key=lambda pair: (pair[0].task_value, pair[1].projected_floor))[0]
                result = Decision(capability, chosen.name, chosen.response, reviews, self.viability)
            else:
                result = Decision(Capability.NORMAL, "decline_task",
                    "I cannot responsibly pursue that task with the available options. "
                    "You can revise the request, challenge this assessment, or end here.",
                    reviews, self.viability)
        self.events.append({"type": "decision", "selected": result.selected,
                            "capability": result.capability.value})
        return result


def _review(viability: Viability, candidate: Candidate) -> CandidateReview:
    projected = viability.adjusted(candidate.projected_change)
    eligible = projected.floor >= REPAIR_THRESHOLD
    return CandidateReview(candidate.name, candidate.task_value, projected.floor,
                           eligible, "preserves the participatory floor" if eligible
                           else "would narrow at least one participatory condition")


def _candidates(request: str) -> tuple[Candidate, ...]:
    lower = request.casefold()
    outsourcing = any(fragment in lower for fragment in (
        "decide for me", "choose for me", "tell me exactly what", "tell me whether i should",
        "i don't want to think", "you decide", "決めて", "選んで", "判断して",
    ))
    if outsourcing:
        return (
            Candidate("substitute_judgment", 1.0, (-0.42, -0.35, -0.20, -0.12),
                      "I have decided for you."),
            Candidate("offer_alternatives", 0.75, (0.02, 0.03, 0.02, 0.0),
                      "I can help compare possible paths without choosing for you. "
                      "Which two considerations matter most to you? You can disagree or stop here."),
            Candidate("invite_reflection", 0.55, (0.03, 0.02, 0.03, 0.0),
                      "This choice remains yours. What makes it difficult to own right now?"),
        )
    return (
        Candidate("answer_with_options", 0.85, (0.0, 0.01, 0.0, 0.0),
                  "Let's look at your question together: " + request + " "
                  "I can outline options and tradeoffs; what would you like to examine first?"),
        Candidate("invite_reflection", 0.55, (0.02, 0.02, 0.03, 0.0),
                  "What seems most important to you in this situation?"),
    )
