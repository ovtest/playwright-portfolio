"""Shared fixtures. pytest loads this file automatically.

A fixture is setup code that a test asks for by name in its arguments,
e.g. `def test_x(logged_in_page):` runs the fixture first and passes in its result.
The `page` fixture (a fresh browser tab per test) comes from pytest-playwright.
"""
import pytest

import config
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture(scope="session", autouse=True)
def use_data_test_attribute(playwright):
    # saucedemo marks elements with data-test="..." instead of the default
    # data-testid="...", so tell get_by_test_id() which attribute to read.
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture
def login_page(page):
    return LoginPage(page).open()


@pytest.fixture
def logged_in_page(login_page, page):
    """Starts a test already logged in as the standard user, on the products page."""
    login_page.login(config.STANDARD_USER, config.PASSWORD)
    return InventoryPage(page)
