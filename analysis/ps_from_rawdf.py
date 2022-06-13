"""
See `tts_calculation_without_bootstrapping` for a detailed explanation
on how to use the functions defined here.
"""


from math import comb
import pandas as pd
import manipulating_bitstring as mb


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


def restrict_to_bvn(dataframe: pd.DataFrame, seq_list: list, n: int) -> pd.DataFrame:
    """Starting with the raw data, return the success probabilities for ssBV-n

    Args:
        dataframe (pd.DataFrame): dataframes with prefix rawdf
        seq_list (list): list of sequences to extract from rawdf
        n (int): problem size

    Returns:
        pd.DataFrame: DataFrame with marked oracles as rows, seq_list as columns,
        and success probabilities as the entry
    """
    new_df = pd.DataFrame()
    # iterate over each row of the dataframe
    for index, row in dataframe.iterrows():
        if index.count("1") < n + 1:
            mark = index[:n]
            ancilla_q = row["ancillas"]
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

            new_df = pd.concat((new_df, pd.Series(info_raw, name=mark)), axis=1)
    return new_df.transpose()
