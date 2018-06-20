from flagbot import utils

def test_aliases():
    u = utils.utils()
    assert u.alias_valid("@Check")
    assert u.alias_valid("@CheckYerFlags")
    assert u.alias_valid("cf")
    assert u.alias_valid("cyf")

def test_aliases_fail():
    u = utils.utils()
    assert not u.alias_valid("@FlaggersHall")
    assert not u.alias_valid("@House")
    assert not u.alias_valid("@Natty")
    assert not u.alias_valid("@Thunder")