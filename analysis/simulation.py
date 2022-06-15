import qiskit

# TODO: Add typehints and docstrings
def simulate(circ):
    simulator = qiskit.Aer.get_backend("aer_simulator")
    result = qiskit.execute(circ, simulator).result().get_counts()
    return result


def unitary(circ):
    # Select the UnitarySimulator from the Aer provider
    simulator = qiskit.Aer.get_backend("unitary_simulator")

    # Execute and get counts
    circ.remove_final_measurements()
    sim = qiskit.execute(circ, simulator)
    result = sim.result()
    unitary = result.get_unitary(circ)
    return unitary
