import pytest

what_is_the_answer, is_the_answer = lambda x=None: x or 42, lambda x: x == 42
everything = set(range(1, 100))
everything |= set("I like everything about pytest except its speed")
the_data_was_inicialized = False


@pytest.fixture
def the_data():
    global the_data_was_inicialized
    if the_data_was_inicialized:
        raise Exception("The data has already been initialized!")
    the_data_was_inicialized = True
    return "I am the data you don't want to initialize"


def test_the_answer():
    assert what_is_the_answer() == 42


def test_fixtures(the_data):
    assert what_is_the_answer(the_data)


@pytest.mark.xfail(strict=True)
def test_fixtures2(the_data):
    assert what_is_the_answer(the_data) == 42


@pytest.mark.skip()
def test_fixtures3(the_data):
    assert what_is_the_answer(the_data) == 42


@pytest.mark.skipif(True, reason="The cake is a lie")
def test_fixtures4(the_data):
    assert what_is_the_answer(the_data) == 42


@pytest.mark.parametrize("something", everything)
def test_everything(something):
    assert what_is_the_answer(something) == something
