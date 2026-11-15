"""Page Object for the checkout steps (info -> overview -> complete)."""
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Step 1: customer information
        self.first_name = page.get_by_test_id("firstName")
        self.last_name = page.get_by_test_id("lastName")
        self.postal_code = page.get_by_test_id("postalCode")
        self.continue_button = page.get_by_test_id("continue")
        self.error_message = page.get_by_test_id("error")
        # Step 2: overview
        self.finish_button = page.get_by_test_id("finish")
        # Step 3: confirmation
        self.complete_header = page.get_by_test_id("complete-header")

    def fill_customer_info(self, first_name, last_name, postal_code):
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.postal_code.fill(postal_code)
        self.continue_button.click()

    def finish(self):
        self.finish_button.click()
