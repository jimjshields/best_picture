import project
import unittest
from bs4 import BeautifulSoup

class TestPageData(unittest.TestCase):
	"""Tests the PageData class."""

	def setUp(self):
		self.page_data_obj = project.PageData(
			'http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.url_text = self.page_data_obj.get_url_text()
		self.text_soup = self.page_data_obj.get_soup_from_text()

	def test_get_url_text(self):
		"""Tests that the get_url_text method gets unicode back."""

		self.assertTrue(isinstance(self.url_text, unicode))

	def test_get_soup_from_text(self):
		"""Tests that the get_soup_from_text method returns a BeautifulSoup 
		   object."""

		self.assertTrue(isinstance(self.text_soup, BeautifulSoup))

class TestMovieData(unittest.TestCase):
	"""Tests the MovieData class."""

	def setUp(self):
		self.movie_data_obj = project.MovieData(
			'/wiki/The_Silence_of_the_Lambs_%28film%29')
		self.movie_budget_str = self.movie_data_obj.get_movie_budget()
		self.split_budget = self.movie_data_obj.split_budget_text(
			self.movie_budget_str)
		self.movie_budget_int = self.movie_data_obj.convert_budget_to_int(
			self.split_budget)

	def test_get_movie_budget(self):
		"""Tests that the get_movie_budget method returns a unicode repr of 
		   the budget, or 'N/A'."""

		self.assertTrue(isinstance(
			self.movie_budget_str, unicode))

	def test_split_budget_text(self):
		"""Tests that the split_budget_text method returns either a tuple or 
		   u'N/A'."""

		self.assertTrue(type(self.split_budget) in [unicode, tuple])

	def test_convert_budget_to_int(self):
		"""Tests that the convert_budget_to_int method returns either a float 
		   or u'N/A'."""

		self.assertTrue(type(self.movie_budget_int) in [unicode, float])

if __name__ == '__main__':
	unittest.main()