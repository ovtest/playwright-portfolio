"""Login tests: one happy path and a few negative cases."""
import re

import pytest
from playwright.sync_api import expect

import config
from pages.inventory_page import InventoryPage


@pytest.mark.smoke
def test_standard_user_can_log_in(login_page, page):
    login_page.login(config.STANDARD_USER, config.PASSWORD)

    # expect() waits automatically (up to 5s) until the condition is true.
    expect(page).to_have_url(re.compile(r".*/inventory\.html"))
    expect(InventoryPage(page).title).to_have_text("Products")


@pytest.mark.regression
def test_locked_out_user_sees_error(login_page):
    login_page.login(config.LOCKED_OUT_USER, config.PASSWORD)

    expect(login_page.error_message).to_contain_text("locked out")


# parametrize = run the same test with different data (data-driven testing)
@pytest.mark.regression
@pytest.mark.parametrize(
    "username, password, expected_error",
    [
        ("", "", "Username is required"),
        ("standard_user", "", "Password is required"),
        ("standard_user", "wrong_password", "do not match any user"),
    ],
    ids=["empty-form", "missing-password", "wrong-password"],
)
def test_invalid_login_shows_error(login_page, username, password, expected_error):
    login_page.login(username, password)

    expect(login_page.error_message).to_contain_text(expected_error)
