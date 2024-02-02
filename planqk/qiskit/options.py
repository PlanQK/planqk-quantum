from qiskit.providers import Options


class OptionsV2(Options):

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __iter__(self):
        return super().__iter__()

    def __len__(self):
        return super().__len__()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    @property
    def __dict__(self):
        return super().__dict__

    def __getattr__(self, name):
        return super().__getattr__(name)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)

    def __getstate__(self):
        return super().__getstate__()

    def __setstate__(self, state):
        super().__setstate__(state)

    def __copy__(self):
        return super().__copy__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return super().__repr__()

    def __eq__(self, other):
        return super().__eq__(other)

    def set_validator(self, field, validator_value):
        super().set_validator(field, validator_value)

    def update_options(self, **fields):
        super().update_options(**fields)

    def __str__(self):
        return super().__str__()

    @property
    def data(self):
        return list(self.__dict__.keys())

    def update_config(self, **fields):
        super().update_options(**fields)
