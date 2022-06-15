import random
import statistics
import tts_from_rawdf
import pickle
from tqdm import tqdm
import os
import pandas as pd
import numpy as np
from collections import Counter


def countdict_to_replist(countdict):
    replist = []
    for key in list(countdict.keys()):
        # force count to be integers
        for n in range(0, int(round(countdict[key]))):
            replist.append(key)
    return replist


def bootstrapped_copy_replist(replist, samples=None):
    """
    Given a replist like ['00', '00', '01','11','01','00']
    we want to randomly sample from this list and
    create a bootstrapped copy of this replist
    """
    return [random.choice(replist) for i in range(0, len(replist))]


def replist_to_countdict(replist):
    return dict(Counter(replist))


def bootstrapped_copy_countdict(countdict):
    org_replist = countdict_to_replist(countdict)
    new_replist = bootstrapped_copy_replist(org_replist)
    new_countdict = replist_to_countdict(new_replist)
    return new_countdict


def bootstrap(func, data, samples=1000):
    """
    func takes data as its input
    Here data is assumed to be a countdict or a list
    """
    func_sample = []
    if type(data) == dict:
        copy_data = bootstrapped_copy_countdict
    if type(data) == list:
        copy_data = bootstrapped_copy_replist

    for i in range(0, samples):
        data_new = copy_data(data)
        func_new = func(data_new)
        func_sample.append(func_new)
    func_average = [statistics.mean(func_sample), statistics.stdev(func_sample)]
    return func_average


# TODO: Add typehints and docstrings
def generate_bootstrapped_df(raw_df, N: int = 100):
    bootstrapped_df = raw_df.copy()
    seqs = [
        x for x in list(raw_df.columns) if x not in ["ancillas", "marked", "remaining"]
    ]
    for index, rows in raw_df.iterrows():
        for column in seqs:
            old_dataset = dict(rows[column])
            new_dataset = bootstrapped_copy_countdict(old_dataset)
            bootstrapped_df[column][index] = new_dataset
    return bootstrapped_df


def mkdir(path: str) -> None:
    """Generate the directory corresponding to path, if it doesn't exist

    Args:
        path (str): Input: path of the file
    """

    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def export_bootstrapped_tts_from_rawdf(rawdf_fname: str, N: int = 100) -> str:
    """Given a rawdf file, create bootstrapped samples, compute the TTS for
    all problem sizes and the TTS to a subfolder bootstrapped/ that is located
    in the same folder as rawdf.

    Args:
        rawdf_fname (str): location of raw_df
        N (int): number of bootstrapped samples. Defaults to 100.

    Returns:
        str: location of bootstrapped files
    """

    file = open(rawdf_fname, "rb")
    rawdf = pickle.load(file)
    file.close()

    durations_fname = rawdf_fname.replace("rawdf", "durations")
    file = open(durations_fname, "rb")
    durations = pickle.load(file)
    file.close()

    mkdir(rawdf_fname.replace("rawdf", f"bootstrapped/tts_bs-0"))

    for i in tqdm(range(N)):
        bs_rawdf_sample = generate_bootstrapped_df(rawdf)
        bs_tts_sample = tts_from_rawdf.tts_from_rawdf(bs_rawdf_sample, durations)
        bs_tts_file = rawdf_fname.replace("rawdf", f"bootstrapped/tts_bs-{i}").replace(
            ".p", ".csv"
        )
        bs_tts_sample.to_csv(bs_tts_file)

    return rawdf_fname


# Computing average TTS from a list of bootstrapped samples


def tts_list_finite(tts_list: list) -> list:
    """Remove all infinite TTS values from a list

    Args:
        tts_list (list): list of number representing TTS, infinite values are np.nan()

    Returns:
        list: Remove all values that are found to infinite
    """
    finite_tts = []
    for t in tts_list:
        if not np.isnan(t):
            finite_tts.append(t)

    # if there are no finite TTS values then just return the original list
    if len(finite_tts) != 0:
        return finite_tts
    else:
        return tts_list


def average_over_tts_lst(lst: list) -> pd.DataFrame:
    """Return average TTS from a list of TTS DataFrames

    Args:
        lst (list): list of pd.DataFrame with Row = oracles, Columns = DD sequences, Entries = TTS

    Returns:
        pd.DataFrame: Row = oracles, Columns = DD sequences (mean and std), Entries = TTS
    """
    base = lst[0]
    new_pd = pd.DataFrame()
    for r in list(base.index):
        for c in list(base.columns):
            tts_list = tts_list_finite([x[c].loc[r] for x in lst])
            val = np.mean(tts_list)
            err = np.std(tts_list)
            new_pd.at[r, f"{c} mean"] = val
            new_pd.at[r, f"{c} err"] = err
    return new_pd


# TODO: Add typehints and docstrings
def get_all_tts(rawdata_file, n=100):
    lst = []
    for i in range(0, n):
        tts_file = rawdata_file.replace("rawdata", f"bootstrapped/tts_bs-{i}")
        file = open(tts_file, "rb")
        data = pickle.load(file)
        file.close()
        lst.append(data)
    return lst


def extract_avg_tts_from_bs_samples(
    rawdf_fname: str, start: int = 0, samples: int = 100, export: bool = False
) -> pd.DataFrame:
    """

    Args:
        rawdf_fname (str): name of the rawdf file
        start (int, optional): starting bootstrapped sample number. Defaults to 0.
        samples (int, optional): final bootstrapped sample number. Defaults to 100.
        export (bool): to export or not to export the average TTS values. Defaults to False.

    Returns:
        pd.DataFrame: Row = oracles, Columns = DD sequences (mean and std), Entries = TTS
    """
    tts_df_list = []
    for i in range(start, samples):
        tts_fname = rawdf_fname.replace("rawdf", f"bootstrapped/tts_bs-{i}").replace(
            ".p", ".csv"
        )
        tts_sample = pd.read_csv(tts_fname, index_col=0)

        tts_df_list.append(tts_sample)

    avg_tts = average_over_tts_lst(tts_df_list)

    if export == True:
        # export to data folder
        avg_tts_file = rawdf_fname.replace("rawdf", f"avgtts").replace(".p", ".csv")
        avg_tts.to_csv(avg_tts_file)
        # export to results folder
        avg_tts_file_results = "../results/" + os.path.basename(avg_tts_file)
        print(avg_tts_file_results)
        avg_tts.to_csv(avg_tts_file_results)

    return avg_tts
