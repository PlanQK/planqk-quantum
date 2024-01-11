from cmath import exp
from typing import List
from typing import TYPE_CHECKING

from qiskit.circuit import Gate
from qiskit.circuit import Parameter
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary
from qiskit.circuit.library import CPhaseGate
from qiskit.quantum_info import Kraus

if TYPE_CHECKING:
    import qiskit


class PCPGate(Gate):
    r"""Implements the phase-shifted controlled-phase gate (PCP).

    This class implements an idealized version of a controlled-phase gate as it can
    potentially be realized by the Rydberg platform. Similarly to the :class:`PCZGate`,
    the gate is hereby only realized up to single-qubit phase gates. The phase shift
    :math:`\theta` depends on the phase :math:`\lambda` of the gate.

    Unitary matrix representation:

    .. math::

        PCP =
        \begin{pmatrix}
        1 & 0 & 0 & 0 \\
        0 & e^{i\theta(\lambda)} & 0 & 0 \\
        0 & 0 & e^{i\theta(\lambda)} & 0 \\
        0 & 0 & 0 & e^{i(2\theta(\lambda)+\lambda)}
        \end{pmatrix}

    Note that the :math:`\lambda`-dependence that is implemented in this class is only
    accurate for :math:`\lambda \leq \pi`.

    .. testcode::

        from qiskit_qryd_provider import PCPGate
        import numpy as np

        assert np.round(PCPGate.get_theta(np.pi), 2) == 2.13

    """

    def __init__(self, lam: float, label: str = None) -> None:
        """Create a new PCP gate.

        Args:
            lam: Phase of the gate.
            label: Optional label for the gate.

        """
        super().__init__("pcp", 2, [lam], label=label)

    def _define(self) -> None:
        """Define the gate."""
        qc = QuantumCircuit(2)
        lam = self.params[0]
        theta = self.get_theta(lam)
        qc.u(0, 0, theta, 0)
        qc.u(0, 0, theta, 1)
        qc.cp(lam, 0, 1)
        self.definition = qc

    def to_matrix(self) -> List[List[complex]]:
        """Return the unitary matrix of the gate.

        Returns:
            A two-dimensional array for the gate unitary matrix.

        """
        lam = self.params[0]
        theta = self.get_theta(lam)
        return [
            [1, 0, 0, 0],
            [0, exp(1j * theta), 0, 0],
            [0, 0, exp(1j * theta), 0],
            [0, 0, 0, exp(2j * self._theta + 1j * lam)],
        ]

    def to_kraus(self) -> "qiskit.circuit.Instruction":
        """Return the Kraus representation of the gate.

        Raises:
            NotImplementedError: If the Kraus representation is not set.

        Returns:
            An instruction encapsulating the Kraus representation.

        """
        if self._kraus is None:
            raise NotImplementedError("The Kraus representation is not implemented.")
        return self._kraus

    @classmethod
    def _init_theta(cls) -> None:
        r"""Initialize the :math:`\lambda`-dependent phase shift of the gate.

        Note that after the initialization, a
        decomposition of the PCP gate is stored to Qiskit's
        SessionEquivalenceLibrary.

        """
        cls._lam = Parameter("lambda")
        cls._theta = (
            5.11382
            - 0.32933
            * (
                1.63085 * cls._lam * cls._lam * (2 * cls._lam).exp()
                + cls._lam
                + 0.02899
            ).log()
        )

        # Reset equivalence library
        default = []
        for c in SessionEquivalenceLibrary.get_entry(CPhaseGate(cls._lam)):
            if not c.get_instructions("pcp"):
                default.append(c)
        SessionEquivalenceLibrary.set_entry(CPhaseGate(cls._lam), default)

        SessionEquivalenceLibrary.set_entry(PCPGate(cls._lam), [])

        # Attach new decomposition to the equivalence library
        def_pcp_cz = QuantumCircuit(2)
        def_pcp_cz.append(PCPGate(cls._lam), [0, 1])
        def_pcp_cz.u(0, 0, -cls._theta, 0)
        def_pcp_cz.u(0, 0, -cls._theta, 1)
        SessionEquivalenceLibrary.add_equivalence(CPhaseGate(cls._lam), def_pcp_cz)

        def_cz_pcp = QuantumCircuit(2)
        def_cz_pcp.append(CPhaseGate(cls._lam), [0, 1])
        def_cz_pcp.u(0, 0, cls._theta, 0)
        def_cz_pcp.u(0, 0, cls._theta, 1)
        SessionEquivalenceLibrary.add_equivalence(PCPGate(cls._lam), def_cz_pcp)

    @classmethod
    def get_theta(cls, lam: float) -> float:
        r"""Get the phase shift of the gate for a given phase :math:`\lambda`.

        Args:
            lam: Phase of the gate.

        Returns:
            Angle of the phase shift.

        """
        return float(cls._theta.assign(cls._lam, lam))

    @classmethod
    def set_kraus(cls, kraus: List[List[List[complex]]] = None) -> None:
        """Set the Kraus representation of the gate.

        Args:
            kraus: A three-dimensional array encoding the Kraus representation of the
                gate.

        """
        if kraus is not None:
            cls._kraus = Kraus(kraus).to_instruction()
        else:
            cls._kraus = None


PCPGate._init_theta()
PCPGate.set_kraus(None)
