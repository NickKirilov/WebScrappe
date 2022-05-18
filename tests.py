import os
import unittest

from cases import scrape_cases, scrape_cases_details
from notices import scrape_notices, scrape_notices_details


class TestCreatingCsvFiles(unittest.TestCase):
    def test_scrap_notices__expect_success(self):
        scrape_notices()
        self.assertTrue(os.path.exists('Notices/England/England.csv'))

    def test_scrap_notices_paginating__expect_success(self):
        scrape_notices_details()
        self.assertTrue(os.path.exists('Notices/England/312471011.csv'))

    def test_scrap_cases__expect_success(self):
        scrape_cases()
        self.assertTrue(os.path.exists('Cases/ESE/ESE.csv'))

    def test_scrap_cases_paginating__expect_success(self):
        scrape_cases_details()
        self.assertTrue(os.path.exists('Cases/ESE/4544480.csv'))
