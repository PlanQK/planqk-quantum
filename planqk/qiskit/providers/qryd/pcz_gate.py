from cmath import exp
from typing import List
from typing import TYPE_CHECKING

from qiskit.circuit import Gate
from qiskit.circuit import QuantumCircuit
from qiskit.circuit.equivalence_library import SessionEquivalenceLibrary
from qiskit.circuit.library import CXGate
from qiskit.circuit.library import CZGate
from qiskit.quantum_info import Kraus

if TYPE_CHECKING:
    import qiskit


class PCZGate(Gate):
    r"""Implements the phase-shifted controlled-Z gate (PCZ).

    The PCZ gate is the controlled-Z gate up to single-qubit phase gates.
    It can be realized by the Rydberg platform in multiple ways [`1
    <https://doi.org/10.1103/PhysRevLett.123.170503>`__,
    `2 <https://doi.org/10.1103/PhysRevResearch.4.033019>`__,
    `3 <https://doi.org/10.22331/q-2022-05-13-712>`__].

    Unitary matrix representation:

    .. math::

        PCZ =
        \begin{pmatrix}
        1 & 0 & 0 & 0 \\
        0 & e^{i\theta} & 0 & 0 \\
        0 & 0 & e^{i\theta} & 0 \\
        0 & 0 & 0 & e^{i(2\theta-\pi)}
        \end{pmatrix}

    The phase shift :math:`\theta` has the default value 2.13, as calculated
    for experimentally realistic parameters [`2
    <https://doi.org/10.1103/PhysRevResearch.4.033019>`__].
    It can be modified before using the :class:`~qiskit_qryd_provider.QRydProvider` via:

    .. testcode::

        from qiskit_qryd_provider import PCZGate

        PCZGate.set_theta(1.234)

        assert PCZGate.get_theta() == 1.234

    """

    def __init__(self, label: str = None) -> None:
        """Create a new PCZ gate.

        Args:
            label: Optional label for the gate.

        """
        super().__init__("pcz", 2, [], label=label)

    def _define(self) -> None:
        """Define the gate."""
        qc = QuantumCircuit(2)
        qc.u(0, 0, self._theta, 0)
        qc.u(0, 0, self._theta, 1)
        qc.cz(0, 1)
        self.definition = qc

    def to_matrix(self) -> List[List[complex]]:
        """Return the unitary matrix of the gate.

        Returns:
            A two-dimensional array for the gate unitary matrix.

        """
        return [
            [1, 0, 0, 0],
            [0, exp(1j * self._theta), 0, 0],
            [0, 0, exp(1j * self._theta), 0],
            [0, 0, 0, -exp(2j * self._theta)],
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
    def set_theta(cls, theta: float) -> None:
        """Set the phase shift of the gate.

        Note that after setting the phase shift to a new value, an updated
        decomposition of the PCZ gate is stored to Qiskit's
        SessionEquivalenceLibrary.

        Args:
            theta: Angle of the phase shift.

        """
        cls._theta = theta

        # Reset equivalence library
        default = []
        for c in SessionEquivalenceLibrary.get_entry(CXGate()):
            if not c.get_instructions("pcz"):
                default.append(c)
        SessionEquivalenceLibrary.set_entry(CXGate(), default)

        default = []
        for c in SessionEquivalenceLibrary.get_entry(CZGate()):
            if not c.get_instructions("pcz"):
                default.append(c)
        SessionEquivalenceLibrary.set_entry(CZGate(), default)

        SessionEquivalenceLibrary.set_entry(CZGate(), [])

        # Attach new decomposition to the equivalence library
        def_pcz_cz = QuantumCircuit(2)
        def_pcz_cz.append(PCZGate(), [0, 1])
        def_pcz_cz.u(0, 0, -cls._theta, 0)
        def_pcz_cz.u(0, 0, -cls._theta, 1)
        SessionEquivalenceLibrary.add_equivalence(CZGate(), def_pcz_cz)

        def_pcz_cx = QuantumCircuit(2)
        def_pcz_cx.h(1)
        def_pcz_cx.append(PCZGate(), [0, 1])
        def_pcz_cx.u(0, 0, -cls._theta, 0)
        def_pcz_cx.u(0, 0, -cls._theta, 1)
        def_pcz_cx.h(1)
        SessionEquivalenceLibrary.add_equivalence(CXGate(), def_pcz_cx)

        def_cz_pcz = QuantumCircuit(2)
        def_cz_pcz.append(CZGate(), [0, 1])
        def_cz_pcz.u(0, 0, cls._theta, 0)
        def_cz_pcz.u(0, 0, cls._theta, 1)
        SessionEquivalenceLibrary.add_equivalence(PCZGate(), def_cz_pcz)

        def_cx_pcz = QuantumCircuit(2)
        def_cx_pcz.h(1)
        def_cx_pcz.append(CXGate(), [0, 1])
        def_cx_pcz.h(1)
        def_cx_pcz.u(0, 0, cls._theta, 0)
        def_cx_pcz.u(0, 0, cls._theta, 1)
        SessionEquivalenceLibrary.add_equivalence(PCZGate(), def_cx_pcz)

    @classmethod
    def get_theta(cls) -> float:
        """Get the phase shift of the gate.

        Returns:
            Angle of the phase shift.

        """
        return cls._theta

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


PCZGate.set_theta(2.13)
PCZGate.set_kraus(None)
