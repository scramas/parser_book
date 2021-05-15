
def dict_reverse(dict):
    revDict = {}
    d = list(dict.keys())
    d.reverse()
    for str in d:
        revDict[str] = dict[str]
    return revDict
