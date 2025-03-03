import pytest
from ..models import DbConnParams


def test_db_params_model_validation():
    result = DbConnParams(engine="sqlite", name="test.db")
    assert result is not None
    result = DbConnParams(
        engine="mysql",
        driver="pymysql",
        host="localhost",
        port=3306,
        username="root",
        password="pass",
        name="test_db",
    )
    assert result is not None

    with pytest.raises(ValueError):
        result = DbConnParams(engine="sqlite", name="test")

    with pytest.raises(ValueError):
        result = DbConnParams(engine="mysql")

    with pytest.raises(ValueError):
        result = DbConnParams(engine="mysql", driver="pymysql")

    with pytest.raises(ValueError):
        result = DbConnParams(engine="mysql", driver="pymysql", host="localhost")

    with pytest.raises(ValueError):
        result = DbConnParams(engine="mysql", driver="pymysql", host="localhost", port=3306)

    with pytest.raises(ValueError):
        result = DbConnParams(engine="mysql", driver="pymysql", host="localhost", port=3306, username="root")

    with pytest.raises(ValueError):
        result = DbConnParams(
            engine="mysql", driver="pymysql", host="localhost", port=3306, username="root", password="pass"
        )


def test_db_params_model_string():
    result = DbConnParams(engine="sqlite", name="test.db")
    assert result is not None
    assert str(result) == "sqlite:///test.db"


    result = DbConnParams(
        engine="mysql",
        driver="pymysql",
        host="localhost",
        port=3306,
        username="root",
        password="pass",
        name="test_db",
    )
    assert result is not None
    assert str(result) == "mysql+pymysql://root:pass@localhost:3306/test_db"
