import random
import statistics


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
    countdict = {}
    for key in list(set(replist)):
        count = sum(1 for x in replist if x == key)
        countdict[key] = count
    return countdict


from collections import Counter


def replist_to_countdict_v2(replist):
    return dict(Counter(replist))


def bootstrapped_copy_countdict(countdict):
    org_replist = countdict_to_replist(countdict)
    new_replist = bootstrapped_copy_replist(org_replist)
    new_countdict = replist_to_countdict_v2(new_replist)
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


def generate_bootstrapped_df(raw_df):
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
