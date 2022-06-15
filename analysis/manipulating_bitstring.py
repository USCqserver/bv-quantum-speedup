import itertools

# TODO: Add typehints and docstrings
def generate_all_bitstrings(num):
    """
    Generate all binary strings with num digits
    For n=2, this should return ['00', '01', '10', '11']
    """
    return ["".join(x) for x in list(itertools.product(["0", "1"], repeat=num))]


def check_substr_in_str(string, string_components):
    """
    string is a binary string like 0101000
    sting_components is a list of location and the corresponding bit value
    Eg. string_components = [[0, '0'], [2, '1']] means 0_1 where _ is irrelevant
    """
    # print(string)
    for comp in string_components:
        pos = comp[0]
        val = comp[1]
        # print(f"{pos},{string[pos]}=={val}")
        if string[pos] == val:
            decision = True
        else:
            decision = False
            return decision
    return decision


import sys

sys.path.append("/Users/bibekpokharel/Dropbox/Research/qutil")
from qutil.bootstrapping import countdict_to_replist, replist_to_countdict_v2


def pick_certain_qubits(data, qubits):
    """
    Given a data, pick the counts only for the qubits of concern
    v1 is inefficient for large lists, this will create a sparser output
    """
    rep_list = countdict_to_replist(data)
    new_rep_list = []
    for x in rep_list:
        x_new = "".join([x[i] for i in qubits])
        new_rep_list.append(x_new)
    new_data = replist_to_countdict_v2(new_rep_list)
    return new_data


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    chunked_list = []
    for i in range(0, len(lst), n):
        chunked_list.append(lst[i : i + n])
    return chunked_list


def count_to_prob(data):
    total_counts = sum(list(data.values()))
    new_data = {}
    for k in list(data.keys()):
        new_data[k] = data[k] / total_counts
    return new_data


def flip_qubit_numbering(n, k):
    """
    ibm writes 3210
    we think in 0123
    This translates between the two
    """
    return int(abs(k - n))


def flip_qubit_list(n, k_list):
    return [flip_qubit_numbering(n, k) for k in k_list]


def ps_data(countdict, qubit, value):
    """
    Given
    countdict = {'00':100, '01':200}
    qubit = 1
    value = '0'
    return a new count dictionary that matches the criteria
    new_countdict = {'00':100}
    """
    new_countdict = {}
    keys = list(countdict.keys())
    for k in keys:
        if k[qubit] == value:
            new_countdict[k] = countdict[k]
    return new_countdict


def count_to_prob(data):
    """
    Normalize count dictionary
    """
    total_counts = sum(list(data.values()))
    new_data = {}
    for k in list(data.keys()):
        new_data[k] = data[k] / total_counts
    return new_data


def prob_to_count(data, total_counts=1000):
    """
    from prob to counts
    """
    new_data = {}
    for k in list(data.keys()):
        new_data[k] = int(data[k] * total_counts)
    return new_data
