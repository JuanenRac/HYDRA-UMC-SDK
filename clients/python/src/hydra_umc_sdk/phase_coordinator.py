# =============================================================================
# HYDRA-UMC-SDK - Shared phase coordinator and common dispatch policy
# Copyright (C) 2026 JuanenRac (Electro Hobby 3D) <electrohobby3d@gmail.com>
# GPL-3.0-or-later - see LICENSE
# =============================================================================
"""One coordinator of job phases for every bridge that maps a phase onto a named action.

The UAV, AMR and droid bridges each had their own copy of the same few steps: look up the action of the job phase,
check its parameters, ask ``evaluate_job`` (the fail-closed gate), let the actions that bring the machine to a safe
state through whatever the gate said, and describe the static vocabulary of actions without opening a transport.
``PhaseCoordinator`` holds those steps once; a bridge keeps only what is specific to its machine: its table of actions,
the parameters each action needs, and what it does with the answer.

It never relaxes the gate: a productive action still needs a READY cell and an observed IDLE machine, and an action
that is not in ``safe_actions`` is exactly as refused as before. It is a policy and data boundary, not a motion API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping

from .bridge_contract import BridgeJob, CellState, GateDecision, JobPhase, MachineState, evaluate_job

SCHEMA_VERSION = "1.1"
MODE_PLAN_ONLY = "plan-only"

# A validator receives the (string) parameters of the job and returns the validated values to forward, or raises
# ``ValueError`` with the reason the job is refused. It is the one place that says what an action's parameters mean.
ParameterValidator = Callable[[Mapping[str, str]], Mapping[str, object]]


@dataclass(frozen=True)
class PhaseDecision:
    """The decision for one action, with the validated parameters it was taken on.

    ``parameters`` holds what the gate actually checked, so a transport sends exactly that and not whatever its caller
    passes alongside.
    """

    accepted: bool
    action: str
    reason: str
    parameters: Mapping[str, object] = field(default_factory=dict)
    mode: str = MODE_PLAN_ONLY


@dataclass(frozen=True)
class ActionPlan:
    """Static evidence of the action vocabulary of a bridge, not a discovered device."""

    schema_version: str
    mode: str
    actions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"schema_version": self.schema_version, "mode": self.mode, "actions": list(self.actions)}


class PhaseCoordinator:
    """Map a job phase onto a named action and gate it, the same way for every bridge."""

    def __init__(
        self,
        phase_actions: Mapping[JobPhase, str],
        *,
        safe_actions: frozenset[str] = frozenset(),
        required_parameters: Mapping[str, tuple[str, ...]] | None = None,
        validators: Mapping[str, ParameterValidator] | None = None,
        extra_actions: tuple[str, ...] = (),
    ) -> None:
        self._phase_actions = dict(phase_actions)
        unknown = [phase for phase in self._phase_actions if not isinstance(phase, JobPhase)]
        if unknown:
            raise ValueError(f"phase_actions keys must be JobPhase members, got {unknown!r}")
        self._safe_actions = frozenset(safe_actions)
        self._required = dict(required_parameters or {})
        self._validators = dict(validators or {})
        self._extra_actions = tuple(extra_actions)

    @property
    def safe_actions(self) -> frozenset[str]:
        return self._safe_actions

    def action_for(self, phase: JobPhase) -> str | None:
        return self._phase_actions.get(phase)

    def vocabulary(self) -> tuple[str, ...]:
        """Every action the bridge can name, once each, in the order of the table and then the standalone ones."""
        return tuple(dict.fromkeys((*self._phase_actions.values(), *self._extra_actions)))

    def plan(self) -> ActionPlan:
        """The static vocabulary, without opening any transport."""
        return ActionPlan(SCHEMA_VERSION, MODE_PLAN_ONLY, self.vocabulary())

    def decide(
        self,
        job: BridgeJob,
        cell_state: CellState,
        observed_machine_state: MachineState | None = None,
        *,
        extra_parameters: Mapping[str, object] | None = None,
    ) -> PhaseDecision:
        """The decision for the action of the phase of ``job``.

        ``observed_machine_state`` is what the bridge read from its machine; the claim written in the job is not a
        reading, so without it the shared gate refuses every productive job. ``extra_parameters`` is merged into the
        validated parameters of an accepted or refused decision (a bridge that resolves a target adds it here).
        """

        action = self._phase_actions.get(job.phase)
        if action is None:
            return PhaseDecision(False, "none", "job phase has no mapped action")
        required = self._required.get(action, ())
        missing = [name for name in required if name not in job.parameters]
        if missing:
            return PhaseDecision(False, action, f"missing required parameter(s) for {action}: {', '.join(missing)}")
        validated: dict[str, object] = {}
        validator = self._validators.get(action)
        if validator is not None:
            try:
                validated = dict(validator(job.parameters))
            except ValueError as error:
                return PhaseDecision(False, action, str(error))
        if extra_parameters:
            validated.update(extra_parameters)
        decision = evaluate_job(job, cell_state, observed_machine_state)
        if not decision.allowed and action in self._safe_actions:
            # Bringing the machine to a safe state (coming home, landing, holding) is never refused for the state of the cell
            # or of the machine: the gate is for starting work.
            return PhaseDecision(True, action, f"{action} is always forwarded ({decision.reason})", validated)
        return PhaseDecision(decision.allowed, action, decision.reason, validated)

    def always_forwarded(self, action: str, reason: str) -> PhaseDecision:
        """A standalone request that only ever takes the machine to a safe state (sit, land, disarm, pause)."""
        return PhaseDecision(True, action, f"{reason} - always forwarded regardless of cell/machine state")

    def gated_request(
        self,
        action: str,
        cell_state: CellState,
        machine_state: MachineState,
        *,
        phase: JobPhase = JobPhase.PREPARE,
        source: str = "standalone-request",
    ) -> PhaseDecision:
        """A standalone request that is a productive transition (standing up): it goes through the same gate as a job.

        The decision is taken by ``evaluate_job`` itself, on a minimal job that carries only the state, so the rule has
        one source and cannot drift from the SDK's.
        """

        job = BridgeJob(f"{action.lower()}-request", f"{action.lower()}-request", source, phase, machine_state, {})
        gate: GateDecision = evaluate_job(job, cell_state, machine_state)
        return PhaseDecision(gate.allowed, action, gate.reason)
