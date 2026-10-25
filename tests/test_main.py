from lotto.main import greet


def test_greet_default():
    assert greet() == "Hello, world! (lotto v0.1.0)"


def test_greet_name():
    assert "Ada" in greet("Ada")
