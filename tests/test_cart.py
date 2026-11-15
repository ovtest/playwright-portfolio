"""Cart tests. They use the logged_in_page fixture, so they skip the login steps."""
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"


@pytest.mark.smoke
def test_add_item_updates_cart_badge(logged_in_page):
    logged_in_page.add_to_cart(BACKPACK)

    expect(logged_in_page.cart_badge).to_have_text("1")


@pytest.mark.regression
def test_cart_shows_added_items(logged_in_page, page):
    logged_in_page.add_to_cart(BACKPACK)
    logged_in_page.add_to_cart(BIKE_LIGHT)
    logged_in_page.open_cart()

    expect(CartPage(page).item_names).to_have_text([BACKPACK, BIKE_LIGHT])


@pytest.mark.regression
def test_remove_item_clears_badge(logged_in_page):
    logged_in_page.add_to_cart(BACKPACK)
    logged_in_page.remove_from_cart(BACKPACK)

    expect(logged_in_page.cart_badge).to_be_hidden()
