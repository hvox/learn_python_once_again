import pytest

what_is_the_answer, is_the_answer = lambda x=None: x or 42, lambda x: x == 42
everything = set(range(1, 100))
everything |= set("I like everything about pytest except its speed")


@pytest.fixture
def the_data():
    return "I am the data you don't want to initialize"


def test_the_answer():
    assert what_is_the_answer() == 42


def test_fixtures():
    assert what_is_the_answer(the_data)


@pytest.mark.parametrize("something", everything)
def test_everything(something):
    assert what_is_the_answer(something) == something
