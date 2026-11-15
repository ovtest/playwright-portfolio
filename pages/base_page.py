"""Base class that every page object inherits from.

It stores the Playwright `page` (the browser tab), so each page class
doesn't have to repeat that.
"""
from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page):
        self.page = page
