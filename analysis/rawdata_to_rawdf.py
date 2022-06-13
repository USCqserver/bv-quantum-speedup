"""
See `tts_calculation_without_bootstrapping` for a detailed explanation
on how to use the functions defined here.
"""


from ctypes import Union
from qiskit import QuantumCircuit
import manipulating_bitstring as mb
import numpy as np
import pandas as pd
from simulation import simulate
from tqdm import tqdm


def bv_identify_ancilla_and_active(qc: str) -> list:
    """Identify the marked and the ancilla qubits given a quantum circuit


    Args:
        qc (Union[str, QuantumCircuit]): This can be given as a qasm or a QuantumCircuit object

    Returns:
        list: list of two lists, first for marked qubits, second for the ancilla
    """
    if type(qc) == str:
        # if qc is given as qasm then convert it to a QuantumCircuit object.
        circ = QuantumCircuit().from_qasm_str(qc)
    else:
        circ = qc
    # remove and add measurements to avoid any confusion about the classical registers
    circ.remove_final_measurements()
    circ.measure_all()
    data_dict = simulate(circ)
    marked_entries = []

    # ancilla will be either 0 or 1 so we will get two bitstrings s1 and s2, which will differ at the ancilla
    for k in list(data_dict.keys()):
        if data_dict[k] != 0:
            marked_entries.append(k)
    [s1, s2] = marked_entries
    ancilla = [i for i in range(len(s1)) if s1[i] != s2[i]]
    marked = [i for i in range(len(s1)) if s1[i] == "1"]

    # marked includes the ancilla so remove that from the list
    marked_wo_ancilla = list(set(marked) - set(ancilla))

    # flip the qubit numbers back from the ibm convention which marks last qubit as the 1st qubit
    marked_val = mb.flip_qubit_list(len(s1) - 1, marked_wo_ancilla)
    ancilla_val = mb.flip_qubit_list(len(s1) - 1, ancilla)
    return [marked_val, ancilla_val]


def data_to_raw_df(data: dict) -> pd.DataFrame:
    """

    Args:
        data (dict): data prefixed rawdata, keys are
            `seq_list` : List of sequences used

            `data` : raw data from the backend

            `calibration_data` : calibration data for the backend, taken on the day of the experiment

            `base_circs`: ssBV-n circuits before DD sequences are superimposed

            `ancillas`: qubits that were identified as the ancilla

    Returns:
        pd.DataFrame: rows are marked oracles, columns are
            `free`: ssBV results for the "bare" circuits

            sequence 1 : ssBV results under DD sequence 1

            sequence 2 : ssBV results under DD sequence 2

            `ancillas` : qubits treated as ancillas

            `marked` : qubits that are marked

            `remaining` : unmarked qubits

    """
    bv_data = data["data"]
    seq_list = ["free"] + data["seq_list"]

    bv_data_grouped = []
    bv_data_grouped += mb.chunks(bv_data, len(seq_list))

    chosen_qubits = range(27)
    BV_ancillas = []
    BV_marked = []
    for circ in tqdm(data["base_circs"]):
        [marked_val, ancilla_val] = bv_identify_ancilla_and_active(circ)

        # the ancillas are off by 10 on Toronto, as we only measured 10, 11, 12, 13.. 16
        BV_marked.append(list(np.array(marked_val)))
        BV_ancillas.append(list(np.array(ancilla_val)))

    marks_org = ["0" * (26 - x) + "1" * x for x in range(27)]
    marks = [x[::-1] for x in marks_org]
    raw_df = pd.DataFrame(data=bv_data_grouped, columns=seq_list, index=marks)
    raw_df["ancillas"] = BV_ancillas
    raw_df["marked"] = BV_marked
    raw_df["remaining"] = [
        list(set(chosen_qubits) - set(BV_ancillas[x]) - set(BV_marked[x]))
        for x in range(len(BV_ancillas))
    ]
    return raw_df
