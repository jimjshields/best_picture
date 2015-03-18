# -*- coding: utf-8 -*-

from __future__ import division
import requests, re
from bs4 import BeautifulSoup
from collections import namedtuple

# Because there are only 3 budgets denoted in pounds, I'm hardcoding a dict of just those year's exchange rates.
# Should there be a new one, a KeyError would be thrown.
# Source: http://www.measuringworth.com/datasets/exchangepound/result.php
GDP_TO_USD_DICT = {u'1948': 4.03, u'1981': 2.02, u'2010': 1.55}

class PageData(object):
	"""Stores attributes and methods of getting data from a webpage."""

	def __init__(self, url):
		"""Initializes with the text found at the url and the BeautifulSoup object
		   of that text."""

		self.url = url
		self.text = self.get_url_text()
		self.text_soup = self.get_soup_from_text()
	
	def get_url_text(self):
		"""Given a url, return the text found at that url. Assumes the encoding
		   of the response is the encoding indicated in the HTTP headers."""

		url_response = requests.get(self.url)
		url_text = url_response.text

		return url_text

	def get_soup_from_text(self):
		"""Given url text, gets the text at that url and attempts to convert it to
		   a BeautifulSoup object. Assumes that the text is HTML."""

		text_soup = BeautifulSoup(self.text)

		return text_soup

class MovieData(PageData):
	"""Stores attributes and methods of getting data from a movie's Wiki page."""

	def __init__(self, movie_url, movie_title, movie_year):
		"""Initializes with the attributes retrieved from the Best Picture page,
		   the BeautifulSoup object of the movie's Wiki page, and the data retrieved
		   from the movie's own page."""

		self.movie_url = movie_url
		self.movie_title = movie_title
		self.movie_year = movie_year

		self.page_data = PageData('http://en.wikipedia.org{0}'.format(self.movie_url))
		self.text_soup = self.page_data.text_soup

		self.budget_string = self.get_movie_budget()
		self.split_budget = self.split_budget_text()
		self.budget_int = self.convert_budget_to_int()

	def get_movie_budget(self):
		"""Given the MovieData object of a movie, returns the budget of the movie
		   as a string, or as 'N/A' if not found."""
		
		# Assumes that the movie info will always be found in the first table.
		# Given that it is the first table, I'm comfortable with the assumption
		# that its position won't change.
		movie_info_table_rows = self.text_soup('table')[0]('tr')

		# Assumes that the budget figure will always be preceded by 'Budget,'
		# enclosed in HTML tags.
		budget_pattern = re.compile(r'>Budget<')
		budget_table_rows = [tr for tr in movie_info_table_rows
							if re.search(budget_pattern, unicode(tr))]
		
		if len(budget_table_rows) == 1:
			budget_text = budget_table_rows[0].td.get_text()

			# Assumes that the budget text will only come in this format:
			# budgetstring[footnote num]
			# Gets rid of that footnote if there is one.
			budget = re.sub(r'\[\d+\]*', '', budget_text)
			budget = re.sub(r'\s', ' ', budget, flags=re.UNICODE)
		elif len(budget_table_rows) == 0:
			budget = u'N/A'
		else:
			# No current cases of multiple budgets, but throw an error 
			# should it happen in the future.
			raise ValueError('More than one budget found on {0}.'.format(self.movie_url))

		return budget

	def split_budget_text(self):
		"""Given a string representing a movie's budget, returns a tuple of
		   currency, digits, and units, or 'N/A'."""

		if self.budget_string == u'N/A':
			split_budget = self.budget_string
		else:

			# Assumes that the budget will always be formatted as: 
			# [curr symbol] [ints w/ commas/periods/unicode dashes] [units]
			# Also assumes that there are only two currencies - USD and GBP.
			# Defaults to USD if given (e.g., The King's Speech), otherwise
			# grabs GBP.
			usd_budget_pattern = ur'(.*\$)\s?([\d, \,, \., \u2013]*)\s?(\D*)'
			gbp_budget_pattern = ur'(.*\£)\s?([\d, \,, \., \u2013]*)\s?(\D*)'

			if re.match(usd_budget_pattern, self.budget_string):
				budget_groups = re.match(usd_budget_pattern, self.budget_string)
			elif re.match(gbp_budget_pattern, self.budget_string):
				budget_groups = re.match(gbp_budget_pattern, self.budget_string)

			if budget_groups:
				currency = budget_groups.group(1).strip()

				# Assumes that decimal points are important, but commas are not.
				digits = budget_groups.group(2).replace(',', '').strip()
				units = budget_groups.group(3).strip()
				split_budget = (currency, digits, units)

		return split_budget

	def convert_budget_to_int(self):
		"""Given the budget as either a str 'N/A' or a tuple of (currency, digits,
		   units), returns either 'N/A' or the budget in ones."""

		if self.split_budget == u'N/A':
			converted_budget = self.split_budget
		else:
			currency, digits, units = self.split_budget
				
			# Takes the average of digits formatted like: '6–7'.
			if u'–' in digits:
				first, second = digits.split(u'–')
				digits = (float(first) + float(second))/2

			# Converts GBP to USD.
			if currency == u'£':
				digits = float(digits) * GDP_TO_USD_DICT[self.movie_year]

			# Assumes that the only possible units are millions, and if so, the 
			# string always contains the substring 'million.' This is a fair
			# assumption for now b/c we have the full dataset and that holds.
			if 'million' in units:

				# Float to correctly convert strings like '1.25'.
				converted_budget = float(digits) * 1000000
			else:

				# Float to correctly convert strings like '$2,840,000.'
				# (trailing period).
				converted_budget = float(digits)

		# Throw error if the output doesn't make logical sense.
		# Assumes a movie budget will be at least $10,000.
		if isinstance(converted_budget, float) and converted_budget < 10000:
			raise ValueError('The budget calculated for {0} is {1}; it\'s too small.'.format(self.movie_url, converted_budget))

		return converted_budget

	def build_movie_named_tuple(self):
		"""For a given MovieData object, returns a named tuple of all found data."""

		movie_data = namedtuple('AllMovieData', 'url, title, year, budget_string, budget_int')
		movie_data_tuple = movie_data(self.movie_url, self.movie_title, self.movie_year, self.budget_string, self.budget_int)

		return movie_data_tuple


class BestPicturePageData(PageData):
	"""Stores attributes and methods of getting data from the Best Picture Oscar Wiki page."""

	def __init__(self):
		"""Initializes with the BeautifulSoup object of the Wiki page."""

		self.page_data = PageData('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.text_soup = self.page_data.text_soup
		self.movie_list_generator = self.get_bp_movie_list_generator()

	def convert_li_to_movie_data(self, li):
		"""Given a BeautifulSoup list item object of a prespecified pattern, returns a tuple
		   of movie_url, movie_title, and movie_year."""

		movie_url = li.a['href']
		movie_title = li.a.string

		# Assumes that the year will always be found in parentheses
		# following a </i> tag and prior to a </li> tag.
		year_pattern = re.compile(r'</i>\s+\((.+)\)</li>')
		movie_year = re.search(year_pattern, unicode(li)).group(1)

		return movie_url, movie_title, movie_year

	def get_bp_movie_list_generator(self):
		"""Given the data for the Best Picture Wiki page, returns a generator of 
		   named tuples of the movie urls, titles, and years."""

		tables = self.text_soup('table')

		# By using negative indexing, assumes that it is more likely that other 
		# tables will be added before this table, rather than after it. 
		possible_winners = tables[-2]('li')

		# Assumes that the movie names will always have the year in parentheses
		# following them and uses this pattern to match the list item for each movie.
		winner_pattern = re.compile(r'.+\(.+\)')
		winners = (li for li in possible_winners 
					if re.match(winner_pattern, unicode(li)))

		# Assumes that movies will continue to be structured as list items,
		# with the url, title, and year found in the same place.
		movie_data = namedtuple('MovieData', 'url, title, year')
		for list_item in winners:
			movie_url, movie_title, movie_year = self.convert_li_to_movie_data(list_item)
			yield movie_data(movie_url, movie_title, movie_year)

	def get_bp_movie_data(self):
		"""Using the movie_list_generator, builds an array of named tuples with the
		   url, title, year, budget_string, and budget_int of the movies."""
		
		movies = []
		
		for movie in self.movie_list_generator:
			movie_obj = MovieData(movie.url, movie.title, movie.year)
			movies.append(movie_obj.build_movie_named_tuple())

	def get_average_budget(self):
		"""After retrieving all of the movie data w/ budgets, returns the average
		   budget of movies that provide a budget."""

		self.bp_movie_data = self.get_bp_movie_data()
		movie_budgets = [movie.budget_int for movie in self.bp_movie_data if movie.budget_int != u'N/A']
		average_budget = sum(movie_budgets) / len(movie_budgets)

		return '{:0,.2f}'.format(average_budget)