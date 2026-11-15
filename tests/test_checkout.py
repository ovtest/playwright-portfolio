"""End-to-end checkout: the most important business flow on the site."""
import pytest
from playwright.sync_api import expect

import config
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.mark.smoke
def test_complete_purchase(logged_in_page, page):
    logged_in_page.add_to_cart("Sauce Labs Backpack")
    logged_in_page.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_customer_info(**config.CUSTOMER)
    checkout.finish()

    expect(checkout.complete_header).to_have_text("Thank you for your order!")


@pytest.mark.regression
def test_checkout_requires_first_name(logged_in_page, page):
    logged_in_page.add_to_cart("Sauce Labs Backpack")
    logged_in_page.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_customer_info("", "User", "12345")

    expect(checkout.error_message).to_contain_text("First Name is required")
