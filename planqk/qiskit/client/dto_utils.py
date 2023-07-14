import dataclasses


def init_with_defined_params(cls, data):
    return cls(**{k: v for k, v in data.items() if k in {f.name for f in dataclasses.fields(cls)}})
