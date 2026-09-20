from sqlalchemy import CheckConstraint
from sqlalchemy.orm import configure_mappers

import app.models
from app.core.database import Base


EXPECTED_TABLES = {
    "users",
    "photographers",
    "photos",
    "products",
    "carts",
    "cart_items",
    "orders",
    "order_items",
}


def test_all_required_models_are_registered() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES


def test_model_relationships_configure() -> None:
    configure_mappers()


def test_required_foreign_keys_exist() -> None:
    assert {str(key.target_fullname) for key in Base.metadata.tables["photographers"].foreign_keys} == {
        "users.id"
    }
    assert {str(key.target_fullname) for key in Base.metadata.tables["photos"].foreign_keys} == {
        "photographers.id"
    }
    assert {str(key.target_fullname) for key in Base.metadata.tables["products"].foreign_keys} == {
        "photos.id"
    }
    assert {str(key.target_fullname) for key in Base.metadata.tables["cart_items"].foreign_keys} == {
        "carts.id",
        "products.id",
    }
    assert {str(key.target_fullname) for key in Base.metadata.tables["order_items"].foreign_keys} == {
        "orders.id",
        "products.id",
    }


def test_business_constraints_are_declared() -> None:
    products = Base.metadata.tables["products"]
    cart_items = Base.metadata.tables["cart_items"]
    order_items = Base.metadata.tables["order_items"]

    product_checks = {constraint.name for constraint in products.constraints if isinstance(constraint, CheckConstraint)}
    cart_checks = {constraint.name for constraint in cart_items.constraints if isinstance(constraint, CheckConstraint)}
    order_checks = {constraint.name for constraint in order_items.constraints if isinstance(constraint, CheckConstraint)}

    assert product_checks == {
        "ck_products_price_positive",
        "ck_products_stock_non_negative",
    }
    assert cart_checks == {"ck_cart_items_quantity_positive"}
    assert order_checks == {
        "ck_order_items_quantity_positive",
        "ck_order_items_price_positive",
    }