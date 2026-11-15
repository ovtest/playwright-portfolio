"""Page Object for the products (inventory) page shown after login."""
from pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.title = page.get_by_test_id("title")
        self.items = page.get_by_test_id("inventory-item")
        self.cart_badge = page.get_by_test_id("shopping-cart-badge")
        self.cart_link = page.get_by_test_id("shopping-cart-link")

    def add_to_cart(self, product_name):
        # Find the product card that contains this name, then click its button.
        card = self.items.filter(has_text=product_name)
        card.get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, product_name):
        card = self.items.filter(has_text=product_name)
        card.get_by_role("button", name="Remove").click()

    def open_cart(self):
        self.cart_link.click()
