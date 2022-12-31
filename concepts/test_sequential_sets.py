import sequential_sets
import pytest


@pytest.fixture
def seq_set():
    return sequential_sets.SequentialSet(range(10))


def test_sequential_set(seq_set):
    assert str(seq_set) == "{" + ", ".join(map(str, range(10))) + "}"


def test_sequential_set_index(seq_set):
    assert seq_set.index(4) == 4


def test_sequential_set_count(seq_set):
    assert seq_set.count(4) == 1


def test_sequential_set_len(seq_set):
    assert len(seq_set) == 10


def test_sequential_set_iter(seq_set):
    assert list(seq_set) == list(range(10))


def test_sequential_set_isdisjoint(seq_set):
    assert seq_set.isdisjoint({11})
    assert not seq_set.isdisjoint({9})


def test_sequential_set_xor(seq_set):
    assert set(range(6)) ^ seq_set == {6, 7, 8, 9}


@pytest.fixture
def mut_set():
    return sequential_sets.MutableSequentialSet(range(10))


def test_mutable_set(mut_set):
    assert str(mut_set) == "{" + ", ".join(map(str, range(10))) + "}"


# TODO: support things like
#   mut_set[0], mut_set[1] = mut_set[1], mut_set[0]


def test_mutable_set_pop(mut_set):
    assert mut_set.pop() == 9
    mut_set.extend({9})


@pytest.fixture
def hsh_set():
    return sequential_sets.HashableSequentialSet(range(10))


def test_hashable_set(hsh_set):
    assert str(hsh_set) == "{" + ", ".join(map(str, range(10))) + "}"


def test_hashable_set_hash(hsh_set):
    assert hash(hsh_set) == 45


def test_dyn_set():
    dyn_set = sequential_sets.DynSet(range(10))
    assert str(dyn_set) == "{" + ", ".join(map(str, range(10))) + "}"
    assert dyn_set.index(4) == 4
    assert dyn_set.count(4) == 1
    assert len(dyn_set) == 10
    assert list(dyn_set) == list(range(10))
    assert dyn_set.isdisjoint({11})
    assert not dyn_set.isdisjoint({9})
    assert set(range(6)) ^ dyn_set == {6, 7, 8, 9}
    assert dyn_set.pop() == 9
    assert dyn_set.pop() == 8
    dyn_set.extend([8, 9])
    assert hash(dyn_set) == 45
    with pytest.raises(ValueError):
        dyn_set.add(123)
    with pytest.raises(ValueError):
        dyn_set.reverse()
