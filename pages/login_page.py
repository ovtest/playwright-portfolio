"""Page Object for the login screen.

A Page Object keeps all the "how" (locators, clicks) for one page in one class.
Tests then only describe the "what": login_page.login("user", "pass").
If the page changes, you fix it here once instead of in every test.
"""
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Locators: how to find elements. get_by_test_id reads the site's
        # data-test="..." attributes (configured in tests/conftest.py).
        self.username_input = page.get_by_test_id("username")
        self.password_input = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")
        self.error_message = page.get_by_test_id("error")

    def open(self):
        self.page.goto("/")  # "/" is added to --base-url from pytest.ini
        return self

    def login(self, username, password):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
