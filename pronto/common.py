import dill


def dill_dump(obj, filepath):
    with open(filepath, "wb") as f:
        dill.dump(obj, f)


def dill_load(filepath):
    with open(filepath, "rb") as f:
        return dill.load(f)
