import project
import unittest
from bs4 import BeautifulSoup
from collections import namedtuple

class TestPageData(unittest.TestCase):
	"""Tests the PageData class."""

	def setUp(self):
		self.page_data_obj = project.PageData(
			'http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.url_text = self.page_data_obj.text
		self.text_soup = self.page_data_obj.text_soup

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
			u'/wiki/The_Silence_of_the_Lambs_%28film%29', u'The Silence of the Lambs', u'1991')
		self.budget_string = self.movie_data_obj.budget_string
		self.split_budget = self.movie_data_obj.split_budget
		self.budget_float = self.movie_data_obj.budget_float

	def test_get_movie_budget(self):
		"""Tests that the get_movie_budget method returns a unicode repr of 
		   the budget, or 'N/A'."""

		self.assertTrue(isinstance(
			self.budget_string, unicode))
		self.assertEqual(self.budget_string, u'$19 million')

	def test_split_budget_text(self):
		"""Tests that the split_budget_text method returns either a tuple or 
		   u'N/A'."""

		self.assertTrue(type(self.split_budget) in [unicode, tuple])
		self.assertEqual(self.split_budget, ('$', '19', 'million'))

	def test_convert_split_budget_to_float(self):
		"""Tests that the convert_budget_to_float method returns either a float 
		   or u'N/A'."""

		self.assertTrue(type(self.budget_float) in [unicode, float])
		self.assertEqual(self.budget_float, (19000000.0))

class TestBestPictureData(unittest.TestCase):
	"""Tests the BestPictureData class."""

	def setUp(self):
		self.bp_data_obj = project.BestPicturePageData()
		self.mock_li = BeautifulSoup(
			'<li><i><a href="/wiki/Wings_(1927_film)" title="Wings (1927 film)">Wings</a></i> (1927/28)</li>')

	def test_convert_li_to_movie_data(self):
		"""Tests that the convert_li_to_movie_data converts a BeautifulSoup
		   li object for a movie to a tuple of appropriate data."""

		self.assertEqual(self.bp_data_obj.convert_li_to_movie_data(self.mock_li), 
			(u'/wiki/Wings_(1927_film)', u'Wings', u'1927/28'))

	def test_get_bp_movie_list_generator(self):
		"""Tests that the get_bp_movie_list_generator returns a generator of named
		   tuples for all Best Picture winners."""

		self.assertTrue(self.bp_data_obj.get_bp_movie_list_generator())

	def test_bp_movie_generator_data(self):
		"""Tests that the first named tuple returned by the generator is exactly as expected.
		   This data should never change; if it did, it would signal a problem."""

		first_item = self.bp_data_obj.get_bp_movie_list_generator().next()
		self.assertEqual(first_item.url, u'/wiki/Wings_(1927_film)')
		self.assertEqual(first_item.title, u'Wings')
		self.assertEqual(first_item.year, u'1927/28')

	def test_bp_movie_list_length(self):
		"""Tests that there are the correct number of movies provided in the generator.
		   This is a fragile test, but only has to change once a year."""

		self.assertEqual(len(list(self.bp_data_obj.get_bp_movie_list_generator())), 87)

	def test_get_average_budget(self):
		"""Tests that the get_average_budget method works as expected, and ignores
		   any unavailable budgets. Uses mock named tuples."""

		movie_data = namedtuple('AllMovieData', 'url, title, year, budget_string, budget_float')
		
		silence = movie_data(
			u'/wiki/The_Silence_of_the_Lambs_%28film%29', u'The Silence of the Lambs', u'1991', u'$19 million', 19000000.0)
		apartment = movie_data(
			u'/wiki/The_Apartment', u'The Apartment', u'1960', u'$3 million', 3000000.0)

		# Movie without budget.
		melody = movie_data(
			u'/wiki/The_Broadway_Melody', u'The Broadway Melody', u'1928/29', u'N/A', u'N/A')

		bp_movie_data = [silence, apartment, melody]

		self.assertEqual(self.bp_data_obj.get_average_budget(bp_movie_data), 11000000.0)

if __name__ == '__main__':
	unittest.main()