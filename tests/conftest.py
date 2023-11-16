# This file is used to configure pytest

def pytest_collection_modifyitems(config, items):
    """
    Ensures that abstract test cases are not being executed.
    """
    for item in items.copy():
        func = item.obj
        if getattr(func, "__isabstractmethod__", False):
            items.remove(item)
