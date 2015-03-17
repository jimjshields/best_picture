import project
import unittest
from bs4 import BeautifulSoup

class PageData(unittest.TestCase):
	"""Tests the PageData class."""

	def setUp(self):
		self.page_data_obj = project.PageData('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.url_text = self.page_data_obj.get_url_text()
		self.text_soup = self.page_data_obj.get_soup_from_text()

	def test_get_url_text(self):
		"""Tests that the get_url_text method gets unicode text back."""

		self.assertTrue(isinstance(self.url_text, unicode))

	def test_get_soup_from_text(self):
		"""Tests that the get_soup_from_text method returns a BeautifulSoup object."""

		self.assertTrue(isinstance(self.text_soup, BeautifulSoup))

if __name__ == '__main__':
	unittest.main()