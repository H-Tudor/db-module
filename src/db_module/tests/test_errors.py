from ..errors import MissingEntry, DuplicateEntry


def test_missing_exception_msg():
    e = MissingEntry("Test", 1)
    assert str(e) == "Missing Test (1)"


def test_duplicate_exception_msg():
    e = DuplicateEntry("Test", 1)
    assert str(e) == "Duplicate Test (1)"
