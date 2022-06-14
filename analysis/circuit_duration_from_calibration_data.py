from qiskit.transpiler import InstructionDurations
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import ALAPSchedule
from qiskit import QuantumCircuit
import pickle


def durations_from_backend(backend_properties):
    """Construct an :class:`InstructionDurations` object from the backend.

    Args:
        backend: backend from which durations (gate lengths) and dt are extracted.

    Returns:
        InstructionDurations: The InstructionDurations constructed from backend.

    Raises:
        TranspilerError: If dt and dtm is different in the backend.
    """
    # All durations in seconds in gate_length
    instruction_durations = []
    for gate, insts in backend_properties["_gates"].items():
        for qubits, props in insts.items():
            if "gate_length" in props:
                gate_length = props["gate_length"][0]  # Throw away datetime at index 1
                instruction_durations.append((gate, qubits, gate_length, "s"))
    for q, props in backend_properties["_qubits"].items():
        if "readout_length" in props:
            readout_length = props["readout_length"][
                0
            ]  # Throw away datetime at index 1
            instruction_durations.append(("measure", [q], readout_length, "s"))

    return InstructionDurations(instruction_durations, dt=2.2222222222222221e-10)


def circuit_duration(
    qasm: str,
    backend_properties: dict,
    dt=2.2222222222222221e-10,
    unit="dt",
):
    """compute circuit duration given the backend properties

    Args:
        qasm (str): qasm representing the circuit
        backend_properties (dict): calibration data fed as a dictionary
        dt (_type_, optional): dt for the backend. Defaults to 2.2222222222222221e-10.
        unit (str, optional): unit of time used takes "dt" or "s". Defaults to "dt".

    Returns:
        _type_: _description_
    """
    qc = QuantumCircuit()
    qc = qc.from_qasm_str(qasm)
    durations = durations_from_backend(backend_properties)
    sched_pass = PassManager([ALAPSchedule(durations)])

    qc_sched = sched_pass.run(qc)
    if unit == "dt":
        return qc_sched.duration
    if unit == "s":
        return (qc_sched.duration) * dt


def export_circuit_duration_from_rawdata(rawdata_fname: str) -> dict:
    """Given a rawdata file, find the calibration data, compute the circuit duration for
    all problem sizes and export the information the same location where the rawdata is located.

    Args:
        rawdata_fname (str): location of the rawdata file

    Returns:
        dict: {n:circuit duration in s}
    """
    file = open(rawdata_fname, "rb")
    rawdata = pickle.load(file)
    file.close()

    prop = rawdata["calibration_data"]
    circuits = rawdata["base_circs"]
    bv_durations = {
        i: circuit_duration(circuits[i], prop, unit="s")
        for i in range(len(rawdata["base_circs"]))
    }
    bv_durations_name = rawdata_fname.replace("rawdata", "durations")
    file = open(bv_durations_name, "wb")
    pickle.dump(bv_durations, file)
    file.close()

    return bv_durations
