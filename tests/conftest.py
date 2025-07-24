import pytest
from db import Base, engine


@pytest.fixture(autouse=True)
def reset_db():
    """Clean database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
