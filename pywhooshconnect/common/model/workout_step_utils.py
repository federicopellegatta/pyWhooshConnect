from abc import ABC
from typing import Generic, List, TypeVar

from pywhooshconnect.common.model.generic_workout import GenericWorkoutStep

T = TypeVar("T", bound=GenericWorkoutStep)


class StepContainerMixin(ABC, Generic[T]):
    """
    Mixin for managing a list of GenericWorkoutStep steps with automatic step_id reindexing.

    Attributes:
        steps (List[T]): The list of contained steps.
    """

    steps: List[T]

    def add_step(self, step: T) -> None:
        """Add a new step at the end of the list and reindex step_ids."""
        self.steps.append(step)
        self.reindex_steps()

    def remove_step(self, step_id: int | None = None) -> None:
        """
        Remove the last step or a specific step by step_id, then reindex step_ids.

        Args:
            step_id (int | None): The step_id of the item to remove.
                                  If None, removes the last item.
        """
        if step_id is not None:
            self.steps = [i for i in self.steps if i.step_id != step_id]
        elif self.steps:
            self.steps.pop()
        else:
            raise ValueError("No steps to remove.")
        self.reindex_steps()

    def sort_steps_by_id(self) -> None:
        """Sort steps by their step_id in ascending order."""
        self.steps.sort(key=lambda step: step.step_id)

    def reindex_steps(self) -> None:
        """Sort steps by step_id and reassign sequential step_ids starting from 1."""
        self.sort_steps_by_id()
        for idx, item in enumerate(self.steps, start=1):
            item.step_id = idx
