"""
See `tts_calculation_without_bootstrapping` for a detailed explanation
on how to use the functions defined here.
"""


from math import comb
import pandas as pd
import manipulating_bitstring as mb
import numpy as np


def get_value(dict: dict, key: str) -> float:
    """return the count if key exists, if not return 0

    Args:
        dict (dict): count_dictionary
        key (str): bitstring

    Returns:
        float: acquired value
    """
    try:
        val = dict[key]
    except KeyError:
        val = 0
    return val


def bv_prob(prob_list: list) -> float:
    """prob_list goes in order
    We want to calculate what the effective probability would be
    once we weight each string for how many time it occurs


    Args:
        prob_list (list): list of probabilities ordered as 000, 001, 011, 111

    Returns:
        float: average probability
    """
    N = len(prob_list)
    n = N - 1
    probs = [comb(n, x) * prob_list[x] for x in range(N)]
    return sum(probs) / 2**n


def restrict_to_bvn(
    dataframe: pd.DataFrame, seq_list: list, n: int, all_counts: bool = False
) -> pd.DataFrame:
    """Starting with the raw data, return the success probabilities for ssBV-n

    Args:
        dataframe (pd.DataFrame): dataframes with prefix rawdf
        seq_list (list): list of sequences to extract from rawdf
        n (int): problem size
        all_counts(bool): False means export only p_s, True means export all the count

    Returns:
        pd.DataFrame: DataFrame with marked oracles as rows, seq_list as columns,
        and success probabilities as the entry
    """
    new_df = pd.DataFrame()
    # iterate over each row of the dataframe
    for index, row in dataframe.iterrows():
        if index.count("1") < n + 1:
            mark = index[:n]

            marked_q = row["marked"]
            remaining_q = row["remaining"]
            chosen_q = marked_q + remaining_q[: n - len(marked_q)]
            chosen_q_ibm = mb.flip_qubit_list(26, chosen_q)

            info_raw = {}
            for seq in seq_list:
                data_org = row[seq]
                data_new = mb.pick_certain_qubits(data_org, chosen_q_ibm)
                data_prob = mb.count_to_prob(data_new)

                counts = get_value(data_prob, mark)
                info_raw[seq] = counts
            if all_counts:
                new_df = pd.concat((new_df, pd.Series(data_prob, name=mark)), axis=1)
            else:
                new_df = pd.concat((new_df, pd.Series(info_raw, name=mark)), axis=1)
    return new_df.transpose()

    # """
    # for instance
    #     00 01 10 11
    # 00
    # 01
    # 11
    # will have row 10 added
    # """


from itertools import permutations


def all_permutations(bitstring):
    return list(set(["".join(x) for x in permutations(bitstring)]))


def apply_permutation_mapping(org, mapping):
    new_lst = [org[mapping[i]] for i in range(len(org))]
    # print(new_lst)
    new = "".join(new_lst)
    return new


def findOccurrences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


def infer_permutation_mapping(org, new):
    """
    010 -> 001
    {0:0, 1:2, 2:1}
    """
    map_dict = {}
    loc_org = findOccurrences(org, "1")
    # print(loc_org)
    loc_new = findOccurrences(new, "1")
    # print(loc_new)
    assert len(loc_org) == len(loc_new)
    # iterate over all indices that have a 1
    for i in range(len(loc_org)):
        org_i = loc_org[i]
        new_i = loc_new[i]
        map_dict[new_i] = org_i

    loc_org_0 = list(set(range(len(org))) - set(loc_org))
    loc_new_0 = list(set(range(len(new))) - set(loc_new))
    # leave the rest intact
    for i in range(len(loc_org_0)):
        org_i = loc_org_0[i]
        new_i = loc_new_0[i]
        map_dict[new_i] = org_i
        # map_dict[new_i] = org_i

    return map_dict


def permuted_list_of_all_bitstrings(org, new):
    # 01 -> 10 gives {0: 1, 1: 0}
    mapping = infer_permutation_mapping(org, new)
    old_strings = mb.generate_all_bitstrings(len(org))
    new_strings = [apply_permutation_mapping(x, mapping) for x in old_strings]
    permutation_map = {}
    for x in range(len(old_strings)):
        permutation_map[old_strings[x]] = new_strings[x]
    return permutation_map


def expand_bv_df_to_all_marks(dataframe: pd.DataFrame) -> pd.DataFrame:

    df_expanded = pd.DataFrame()
    for index, row in dataframe.iterrows():
        # 01 -> 01 and 10
        all_perms = all_permutations(index)

        for bitstring in all_perms:
            new_names = permuted_list_of_all_bitstrings(index, bitstring)
            new_row = row.rename(new_names)
            new_row.name = bitstring
            df_expanded = pd.concat((df_expanded, new_row), axis=1)
            # df_expanded = df_expanded.append(new_row)

    # reorder the list
    all_strings = mb.generate_all_bitstrings(len(bitstring))
    df_final = pd.DataFrame()
    for mark in all_strings:
        df_final = df_final.append(df_expanded[mark])
    df_final = df_final.replace(np.nan, 0)
    return df_final
