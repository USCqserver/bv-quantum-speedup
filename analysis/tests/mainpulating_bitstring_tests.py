def check_substr_in_str_test():
    str1 = '011010'
    str2 = '1010111'
    string_comp1 = [[0, '0'], [3, '0'], [1, '1']]
    string_comp2 = [[1, '0'], [2, '0'], [4, '1']]
    assert (check_substr_in_str(str1, string_comp1) == True)
    assert (check_substr_in_str(str2, string_comp2) == False)
    return None

def pick_certain_qubits_test():
    assert (pick_certain_qubits({
        '00': 10,
        '10': 5,
        '11': 20
    }, [0]) == {
        '0': 10,
        '1': 25
    })
    assert (pick_certain_qubits({
        '00': 10,
        '10': 5,
        '11': 20
    }, [1]) == {
        '0': 15,
        '1': 20
    })
    assert (pick_certain_qubits({'00': 10, '10': 5}, [1]) == {'0': 15})
    return None


def flip_qubit_numbering_test():
    assert (flip_qubit_numbering(3, 0) == 3)
    assert (flip_qubit_numbering(3, 3) == 0)
    assert (flip_qubit_numbering(3, 2) == 1)
    return None

def ps_data_test():
    assert (ps_data({'00': 100, '01': 200}, 1, '0') == {'00': 100})
    assert (ps_data(
        {
            '000': 69,
            '001': 29,
            '010': 25,
            '011': 86,
            '100': 94,
            '101': 47,
            '110': 43,
            '111': 11
        }, 2, '1') == {
            '001': 29,
            '011': 86,
            '101': 47,
            '111': 11
        })
    return None