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
	"""Stores attributes and methods of getting data from any webpage."""

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

	def __init__(self, url, title, year):
		"""Initializes with the attributes retrieved from the Best Picture page,
		   the BeautifulSoup object of the movie's Wiki page, and the data retrieved
		   from the movie's own page."""

		self.url = url
		self.title = title
		self.year = year

		self.page_data = PageData('http://en.wikipedia.org{0}'.format(self.url))
		self.text_soup = self.page_data.text_soup

		self.budget_string = self.get_movie_budget()
		self.split_budget = self.split_budget_text()
		self.budget_float = self.convert_split_budget_to_float()

	def get_movie_budget(self):
		"""Given the MovieData object of a movie, returns the budget of the movie
		   as a string, or as 'N/A' if not found."""
		
		# Assumes that the budget figure will always be preceded by 'Budget,'
		# enclosed in HTML tags.
		budget_pattern = re.compile(r'>Budget<')

		# Assumes that the movie info table will always be HTML class 'infobox'.
		movie_info_table_rows = self.text_soup.find('table', class_='infobox')('tr')
		budget_table_rows = [tr for tr in movie_info_table_rows
							if re.search(budget_pattern, unicode(tr))]
		
		if len(budget_table_rows) == 1:
			budget_text = budget_table_rows[0].td.get_text()

			# Assumes that the budget text will only come in this format:
			# budgetstring[footnote num]
			# Deletes that footnote if there is one.
			budget = re.sub(r'\[\d+\]{1,}', '', budget_text)

			# Deletes any spacing, unicode or otherwise.
			budget = re.sub(r'\s', ' ', budget, flags=re.UNICODE)
		elif len(budget_table_rows) == 0:
			budget = u'N/A'
		else:

			# No current cases of multiple budgets, but throw an error 
			# should it happen in the future.
			raise ValueError('More than one budget found on {0}.'.format(self.url))

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

	def convert_split_budget_to_float(self):
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

			# Converts GBP to USD if only GBP is given.
			if currency == u'£':
				digits = float(digits) * GDP_TO_USD_DICT[self.year]

			# Assumes that the only possible units are millions, and if so, the 
			# string always contains the substring 'million.' This is a fair
			# assumption for now as it applies to the full dataset as of now.
			if 'million' in units:

				# Float to correctly convert strings like '1.25'.
				converted_budget = float(digits) * 1000000
			else:

				# Float to correctly convert strings like '2,840,000.'
				# (trailing period).
				converted_budget = float(digits)

		# Raise ValueError if the output doesn't make logical sense.
		# Assumes a movie budget will be at least $10,000.
		if isinstance(converted_budget, float) and converted_budget < 10000:
			raise ValueError('The budget calculated for {0} is {1}; it\'s too small.'.format(self.url, converted_budget))

		return converted_budget

	def build_movie_named_tuple(self):
		"""For a given MovieData object, returns a named tuple of all found data."""

		movie_data = namedtuple('AllMovieData', 'url, title, year, budget_string, budget_float')
		movie_data_tuple = movie_data(self.url, self.title, self.year, self.budget_string, self.budget_float)

		return movie_data_tuple

class BestPicturePageData(PageData):
	"""Stores attributes and methods of getting data from the Best Picture Oscar Wiki page."""

	def __init__(self):
		"""Initializes with the BeautifulSoup object of the Wiki page and a generator of 
		   all of the urls, titles, and years of the BP winners."""

		self.page_data = PageData('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.text_soup = self.page_data.text_soup
		self.movie_list_generator = self.get_bp_movie_list_generator()

	def convert_li_to_movie_data(self, li):
		"""Given a BeautifulSoup list item object of a prespecified pattern, returns a tuple
		   of url, title, and year."""

		url = li.a['href']
		title = li.a.string

		# Assumes that the year will always follow this pattern:
		# </i>(year)</li>
		year_pattern = re.compile(r'</i>\s+\((.+)\)</li>')
		year = re.search(year_pattern, unicode(li)).group(1)

		return url, title, year

	def get_bp_movie_list_generator(self):
		"""Given the data for the Best Picture Wiki page, returns a generator of 
		   named tuples of the movie urls, titles, and years."""

		tables = self.text_soup('table')

		# By using negative indexing, assumes that it is more likely that other 
		# tables will be added before this table, rather than after it. 
		# Unfortunately there's no more unique identifier for this table.
		possible_winners = tables[-2]('li')

		# Assumes that the movie titles will always follow this pattern:
		# movie title (year/optional second year)
		winner_pattern = re.compile(r'.+\(.+\)')
		winners = (li for li in possible_winners 
					if re.match(winner_pattern, unicode(li)))

		# Assumes that movies will continue to be structured as list items,
		# with the url, title, and year found in the same place.
		movie_data = namedtuple('MovieData', 'url, title, year')
		for list_item in winners:
			url, title, year = self.convert_li_to_movie_data(list_item)
			yield movie_data(url, title, year)

	def get_bp_movie_data(self):
		"""Using the movie_list_generator, builds an array of named tuples with the
		   url, title, year, budget_string, and budget_float of the movies."""
		
		movies = []
		
		for movie in self.movie_list_generator:
			movie_obj = MovieData(movie.url, movie.title, movie.year)
			movie_named_tuple = movie_obj.build_movie_named_tuple()

			# Print here to get better responsiveness. Otherwise would have to wait for the
			# entire table to be built (~30s).
			print u'{title: <50} {year: <10} {budget_string: <15}'.format(
				title=movie_named_tuple.title, year=movie_named_tuple.year, budget_string=movie_named_tuple.budget_string)

			movies.append(movie_named_tuple)

		# This will change once a year. Included it here instead of in testing because this particular
		# array takes too long to build (~30s).
		assert len(movies) == 87

		return movies

	def get_average_budget(self, bp_movie_data):
		"""Given the movie data as an array of named tuples, returns the average
		   budget in USD of movies that provide a budget."""

		movie_budgets = [movie.budget_float for movie in bp_movie_data if movie.budget_float != u'N/A']
		average_budget = sum(movie_budgets) / len(movie_budgets)

		return average_budget

if __name__ == '__main__':
	bp_data_obj = BestPicturePageData()

	# Running this method will print out all the titles, years, budgets as it's building the array.
	bp_movie_data = bp_data_obj.get_bp_movie_data()
	print '------------------'
	print 'Average budget: {:0,.2f}'.format(bp_data_obj.get_average_budget(bp_movie_data))