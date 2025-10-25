import os


def test_env_example_exists():
    assert os.path.exists(os.path.join(os.path.dirname(__file__), "..", ".env.example"))
