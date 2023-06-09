"""
Generic Decentralised Solver
============================

This file specifies the base Solver class which defines the base structure
of the decentralised solver architecture.
"""

from typing import List


from cetpy.Modules.SysML import ValuePrinter


class Solver:
    """Decentralised Solver of the Congruent Engineering Toolbox."""

    __slots__ = ['_recalculate', '_calculating', '_hold', '_resetting',
                 '_name', 'parent', 'convergence_keys', '_tolerance']

    print = ValuePrinter()

    def __init__(self, parent, tolerance: float):
        self._recalculate = False
        self._calculating = False
        self._resetting = False
        self._hold = 0
        self.convergence_keys: List[str] = []
        self.parent = parent
        if parent is not None and self not in parent.solvers:
            parent.solvers += [self]
        self._tolerance = 0
        self.tolerance = tolerance

    # region Interface Functions
    def __set_name__(self, instance, name):
        self._name = name
        self.parent = instance
        if self not in instance.solvers:
            instance.solvers += [self]

    def reset(self, parent_reset: bool = True) -> None:
        """Tell the solver to resolve before the next value output."""
        if not self._resetting:
            self._resetting = True
            self._recalculate = True
            # Reset parent instance if desired
            if parent_reset:
                self.parent.reset()
            self._resetting = False

    def hard_reset(self, convergence_reset: bool = False) -> None:
        """Reset the in progress solver flags and call a normal reset."""
        self._resetting = False
        self._calculating = False
        self.reset()
        if convergence_reset:
            for key in self.convergence_keys:
                self.__setattr__(key, None)
    # endregion

    # region Solver Flags
    @property
    def solved(self) -> bool:
        """Return bool if the solver is solved."""
        return not self._recalculate

    @property
    def calculating(self) -> bool:
        """Return bool if the solver is currently running."""
        return self._calculating

    @property
    def solved_calculating(self) -> bool:
        """Return bool if the solver is solved or currently running."""
        return self.solved or self.calculating

    @property
    def hold(self) -> bool:
        """Current hold status. Hold enables an additional user input to
        enable and disable the automatic run of individual solvers. The hold is
        stored as an integer enabling nested holds throughout the system.

        See Also
        --------
        Solver.raise_hold
        Solver.lower_hold
        """
        return bool(self._hold)

    @hold.setter
    def hold(self, val: (bool, int)) -> None:
        self._hold = int(val)

    def raise_hold(self) -> None:
        """Raise the hold level by one."""
        self._hold += 1

    def lower_hold(self) -> None:
        """Lower the hold level by one."""
        self._hold += 1

    def force_solve(self) -> None:
        """Run the solver, regardless of the current solver state."""
        self._solve()
        # ToDo: Add timing and logging.

    def solve(self) -> None:
        """Run the solver if necessary and allowed.

        The solver will run if the solver is not already solved, the
        solver is not currently already running, and the solver does not
        currently have an enabled hold condition.
        """
        if not self.solved_calculating and not self.hold:
            self.force_solve()
    # endregion

    # region Solver Functions
    def _pre_solve(self) -> None:
        """Conduct standardised pre-run of the solver."""
        self._calculating = True

    def _solve_function(self) -> None:
        """This is the actual solve function of the solver."""
        raise NotImplementedError

    def _post_solve(self) -> None:
        """Conduct standardised post-run of the solver."""
        self._calculating = False
        self._recalculate = False

    def _solve(self) -> None:
        """Private solve function combining the pre-, core-, and post-solve
        functions."""
        self._pre_solve()
        self._solve_function()
        self._post_solve()
    # endregion

    # region Input Properties
    @property
    def tolerance(self) -> float:
        """Solver tolerance."""
        return self._tolerance

    @tolerance.setter
    def tolerance(self, val: float) -> None:
        if val < self._tolerance:
            self.reset()
        self._tolerance = val
    # endregion
