from sqlalchemy import create_engine, inspect

import app.models
from app.core.database import Base


def test_schema_can_be_created_in_isolated_database() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == {
        "users",
        "photographers",
        "photos",
        "products",
        "carts",
        "cart_items",
        "orders",
        "order_items",
    }