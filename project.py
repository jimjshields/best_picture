# -*- coding: utf-8 -*-
"""Overall goal:  scrape the budgets of the Academy Award 
   Best Picture winners from Wikipedia."""

from __future__ import division
import requests, re
from bs4 import BeautifulSoup

class PageData(object):
	"""Stores attributes and methods of getting data from a webpage."""

	def __init__(self, url):
		"""Initializes with the text found at the url, and the BeautifulSoup object
		   of the text."""

		self.text = self.get_url_text(url)
		self.text_soup = self.convert_html_to_bsoup(self.text)
	
	def get_url_text(self, url):
		"""Given a url, return the text found at that url. Assumes the encoding
		   of the response is the encoding indicated in the HTTP headers."""

		# bytestr url => unicode text

		url_response = requests.get(url)
		url_text = url_response.text

		return url_text

	def convert_html_to_bsoup(self, url_text):
		"""Given url text, gets the text at that url and attempts to convert it to
		   a BeautifulSoup object. Assumes that the text is HTML."""

		# unicode text => BeautifulSoup object

		text_soup = BeautifulSoup(url_text)

		return text_soup

class BestPicturePageData(PageData):
	"""Stores attributes and methods of getting data from the Best Picture Oscar Wiki page."""

	def __init__(self):
		"""Initializes with the BeautifulSoup object of the Wiki page."""

		self.page_data = PageData('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
		self.text_soup = self.page_data.text_soup

	def convert_li_to_movie_data(self, li):
		"""Given a BeautifulSoup li object of a prespecified pattern, returns a list
		   of movie_url, movie_title, and movie_year."""

		movie_url = li.a['href']
		movie_title = li.a.string

		# Assumes that the year will always be found in parentheses
		# following a </i> tag and prior to a </li> tag.

		year_pattern = re.compile(r'</i>\s+\((.+)\)</li>')
		movie_year = re.search(year_pattern, unicode(li)).group(1)
		return [movie_url, movie_title, movie_year]

	def get_bp_movie_data(self):
		"""Specific to the Academy Award Best Picture Wiki page. Assumes that the
		   list of BP winners will always be found in the same table."""

		# unicode text => array of unicode text

		tables = self.text_soup('table')

		# By using negative indexing, assumes that it is more likely that other 
		# tables will be added before this table, rather than after it. 
		possible_winners = tables[-2]('li')

		# Assumes that the movie names will always have the year in parentheses
		# following them and uses this pattern to match the list item for each movie.
		winner_pattern = re.compile(r'.+\(.+\)')
		winners = (li for li in possible_winners 
					if re.match(winner_pattern, unicode(li)))

		movies = []

		# Assumes that movies will continue to be structured as list items,
		# with the url, title, and year found in the same place.
		for li in winners:
			movie_data = self.convert_li_to_movie_data(li)
			movies.append(movie_data)
		return movies

class MovieData(PageData):
	"""Stores attributes and methods of getting data from a movie's Wiki page."""

	def __init__(self, movie_url):
		"""Initializes with the BeautifulSoup object of the movie's Wiki page."""

		self.movie_url = movie_url
		self.page_data = PageData('http://en.wikipedia.org{0}'.format(self.movie_url))
		self.text_soup = self.page_data.text_soup
		self.budget = self.get_movie_budget()
		self.split_budget = self.split_budget_text(self.budget)
		self.budget_int = self.convert_budget_to_int(self.split_budget)

	def get_movie_budget(self):
		"""Given the url for a particular movie, returns the budget of the movie
		   as a string, or as 'N/A' if not found."""

		# string url => unicode budget
		
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

			# Assumes that there is only ever one budget.
			# Also assumes that the budget text will only come in this format:
			# budgetstring[footnote num]
			# And gets rid of that footnote if there is one.
			budget_text = budget_table_rows[0].td.get_text()
			budget = re.sub(r'\[\d+\]', '', budget_text)
			budget = re.sub(r'\s', ' ', budget, flags=re.UNICODE)

		elif len(budget_table_rows) == 0: 
			budget = 'N/A'
		else:
			raise ValueError('More than one budget found on {0}.'.format(self.movie_url))

		return budget

	# 4. print out each Year-Title-Budget combination

	def split_budget_text(self, budget_string):
		"""Given a string representing a movie's budget, returns a tuple of
		   currency, digits, and units."""

		if budget_string == 'N/A':
			return budget_string
		else:

			# Assumes that the budget will always be formatted as: 
			# [nonint curr symbol] [ints w/ possible commas\periods] [nonint units]
			budget_pattern = r'(\D*)\s?([\d, \,, \.]*)\s?(\D*)'
			budget_groups = re.match(budget_pattern, budget_string)
			if budget_groups:
				currency = budget_groups.group(1).strip()

				# Assumes that decimal points are important, but commas are not.
				digits = budget_groups.group(2).replace(',', '').strip()
				units = budget_groups.group(3).strip()

				return (currency, digits, units)

	def convert_budget_to_int(self, split_budget):
		"""Given the budget as either a str 'N/A' or a tuple of (currency, digits,
		   units), returns either 'N/A' or the budget in ones."""

		if split_budget == 'N/A':
			return split_budget
		else:
			currency, digits, units = split_budget

			# Assumes that the only possible units are millions, and if so, the 
			# string always contains the substring 'million.' This is a fair
			# assumption for now b/c we have the full dataset and that holds.
				
			# if currency == u'£':

			# 	# TODO: Need to implement conversion function.
			# 	# http://fxtop.com/en/historical-exchange-rates.php?YA=1&C1=GBP&C2=USD&A=1&YYYY1=1953&MM1=01&DD1=01&YYYY2=2015&MM2=03&DD2=16&LANG=en
			# 	digits = float(digits) * gbp_to_usd(year)

			if 'million' in units:

				# Float to correctly convert strings like '1.25 million'.
				return float(digits) * 1000000
			else:

				# Float to correctly convert strings like '$2,840,000.'
				# (trailing period).
				return float(digits)

def get_all_movie_budgets():
	"""Gets all of the Best Picture movie data, and for each movie gets and
	   appends its budget string and budget int to the table, returning the 
	   table."""

	movie_data = get_bp_movie_data()
	for movie in movie_data:
		movie.append(get_movie_budget(movie[0]))
		movie.append(convert_budget_to_int(split_budget_text(movie[3])))

	return movie_data

def get_average_budget():
	"""After retrieving all of the movie data w/ budgets, returns the average
	   budget of movies that provide a budget."""

	movie_data = get_all_movie_budgets()
	movies_with_budgets = [movie for movie in movie_data if movie[4] != 'N/A']
	movie_budgets = [movie[4] for movie in movies_with_budgets]
	budgets_sum = sum(movie_budgets)
	average_budget = budgets_sum / len(movie_budgets)

	return '{:0,.2f}'.format(average_budget)

"""If you encounter any edge cases, feel free to use your best judgement 
and add a comment with your conclusion. This code should be written to 
production standards.

You can use any language you want, but there is a strong preference for a 
language where we will be able to reproduce your results (any modern, 
semi-popular language will be fine). Please add instructions about any 
additional libraries that may be necessary along with versions."""
