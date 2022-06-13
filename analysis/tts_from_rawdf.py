"""
See `tts_calculation_without_bootstrapping` for a detailed explanation
on how to use the functions defined here.
"""

import numpy as np
import pandas as pd
from ps_from_rawdf import bv_prob, restrict_to_bvn
from tqdm import tqdm


def tts(prob: float, dt: float, desired: float = 0.99, unit: str = "log10") -> float:
    """Time to solution given the acquired probability, desired probability, and the time taken

    Args:
        prob (float): acquired probability
        dt (float): time for a single iteration
        desired (float, optional): desired probability. Defaults to 0.99.
        unit (str, optional): seconds or log10 seconds . Defaults to "log10".

    Returns:
        float: Time to solution
    """
    if prob == 0:
        return np.nan  # infinite TTS
    if unit == "default":
        return dt * (np.log(1 - desired) / np.log(1 - prob))
    if unit == "log10":
        return np.log10(tts(prob, dt, unit="default"))


def tts_on_bvn_row(row_data: pd.Series, seq: str, bv_durations: dict) -> float:
    """Given a row from a dataframe of success probabilities and the sequence
    we are concerned with, and the bv_durations compute the sucess probability
    for that particular entry.

    Args:
        row_data (pd.Series): a row from a dataframe of success probabilities
        seq (str): name of the DD sequence
        bv_durations (dict): dictionary representing durations for various BV-n

    Returns:
        float: Time to solution
    """
    bitstring = row_data.name  # get the bitstring like 00000
    no_of_1s = bitstring.count("1")
    duration = bv_durations[no_of_1s]
    prob = row_data[seq]
    # dur = row_data['circuit duration']
    return tts(prob, duration)


def tts_df(bv_n: pd.DataFrame, bv_durations: dict) -> pd.DataFrame:
    """Time to solution given success probabilities and corresponding durations

    Args:
        bv_n (pd.DataFrame): Success probabilities for all the oracles
        bv_durations (dict): Durations for all the oracles

    Returns:
        pd.DataFrame: Same dataframe as `bv_n` but probabilities are replaced with TTS
    """
    seqs = list(bv_n.columns)
    bv_n_tts = pd.DataFrame()
    for seq in seqs:
        bv_n_tts[seq] = bv_n.apply(
            lambda row: tts_on_bvn_row(row, seq, bv_durations), axis=1
        )
    return bv_n_tts


def tts_average(bv_n: pd.DataFrame, bv_durations: dict) -> pd.Series:
    """Averate Time to solution given a dataframe of TTS for each oracle

    Args:
        bv_n (pd.DataFrame): Dataframe with sucess probabilities for each oracle
        bv_durations (dict):  Durations for all the oracles

    Returns:
        pd.Series: Average TTS for each DD sequence
    """
    bv_n_tts = tts_df(bv_n, bv_durations)
    return bv_n_tts.apply(bv_prob)


def tts_average_for_all_n(bv_ns: list, bv_durations: dict) -> pd.DataFrame:
    """Given all the success probabilities and durations (for each oracle in all BV-n)
    return the average TTS for each BV-n

    Args:
        bv_ns (list): list of pd.DataFrame, each representing success probabilities for
            all oracles for a specific n
        bv_durations (dict): Durations for all the oracles

    Returns:
        pd.DataFrame: rows = n, columns = DD Sequence, entries are average TTS
    """

    tts_dataframe = pd.DataFrame()

    for n in range(0, len(bv_ns)):
        bv_n = bv_ns[n]
        tts_n = pd.DataFrame(
            tts_average(bv_n, bv_durations), columns=[n + 1]
        ).transpose()
        tts_dataframe = pd.concat([tts_dataframe, tts_n])

    return tts_dataframe


def tts_from_rawdf(rawdf: pd.DataFrame, bv_durations: dict) -> pd.DataFrame:
    """Time to solution for all sequences and BV-n given the rawdf and the duration.
    This is a composite function, that combines all the other functions in this script.

    Args:
        rawdf (pd.DataFrame): dataframes with prefix rawdf
        bv_durations (dict): Durations for all the oracles

    Returns:
        pd.DataFrame: rows = n, columns = DD Sequence, entries are average TTS
    """
    seqs = list(rawdf.keys()[0:3])  # first 3 elements are the sequences
    N = len(rawdf)  # 27
    ps_df_lst = []
    for n in tqdm(range(1, N)):
        ps_df_lst.append(restrict_to_bvn(rawdf, seqs, n=n))
    tts_all = tts_average_for_all_n(ps_df_lst, bv_durations)
    return tts_all
