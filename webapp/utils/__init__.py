import os


def recursive_listdir(folderpath):
    ret = []
    for x in os.listdir(folderpath):
        fpath = os.path.join(folderpath, x)
        if os.path.isfile(fpath):
            ret.append(fpath)
        else:
            ret.extend(recursive_listdir(fpath))
    return ret
