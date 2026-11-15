"""Page Object for the shopping cart page."""
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.items = page.get_by_test_id("inventory-item")
        self.item_names = page.get_by_test_id("inventory-item-name")
        self.checkout_button = page.get_by_test_id("checkout")

    def checkout(self):
        self.checkout_button.click()
