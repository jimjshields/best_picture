# -*- coding: utf-8 -*-
"""Overall goal:  scrape the budgets of the Academy Award 
   Best Picture winners from Wikipedia."""

from __future__ import division
import requests, re
from bs4 import BeautifulSoup

# 1. Your script should go the the Wikipedia page for the award

def get_url_text(url):
	"""Given a url, return the text found at that url. Assumes the encoding
	   of the response is the encoding indicated in the HTTP headers."""

	# bytestr url => unicode text

	url_response = requests.get(url)
	url_text = url_response.text

	return url_text

def convert_html_to_bsoup(url):
	"""Given a url, gets the text at that url and attempts to convert it to
	   a BeautifulSoup object. Assumes that the text is HTML."""

	# unicode text => BeautifulSoup object

	url_text = get_url_text(url)
	text_soup = BeautifulSoup(url_text)

	return text_soup

def get_bp_movie_data():
	"""Specific to the Academy Award Best Picture Wiki page. Assumes that the
	   list of BP winners will always be found in the same table."""

	# unicode text => array of unicode text

	bp_text_soup = convert_html_to_bsoup(
				'http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
	tables = bp_text_soup('table')

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
		movie_url = li.a['href']
		movie_title = li.a.string

		# Assumes that the year will always be found in parentheses
		# following a </i> tag and prior to a </li> tag.

		# TODO: Separate this out into its own function w/ the budget
		# operations.
		year_pattern = re.compile(r'</i>\s+\((.+)\)</li>')
		movie_year = re.search(year_pattern, unicode(li)).group(1)
		movie_data = [movie_url, movie_title, movie_year]
		movies.append(movie_data)
	return movies

# 2. follow the link for each year’s winner

# 3. grab the budget from the box on the right of the page

def get_movie_budget(movie_url):
	"""Given the url for a particular movie, returns the budget of the movie
	   as a string, or as 'N/A' if not found."""

	# string url => unicode budget

	movie_url_text = get_url_text(
				'http://en.wikipedia.org{0}'.format(movie_url))
	movie_text_soup = BeautifulSoup(movie_url_text)
	
	# Assumes that the movie info will always be found in the first table.
	# Given that it is the first table, I'm comfortable with the assumption
	# that its position won't change.
	movie_info_table_rows = movie_text_soup('table')[0]('tr')

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
		raise ValueError('More than one budget found on {0}.'.format(movie_url))

	return budget

# 4. print out each Year-Title-Budget combination

def split_budget_text(budget_string):
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

def convert_budget_to_int(split_budget):
	"""Given the budget as either a str 'N/A' or a tuple of (currency, digits,
	   units), returns either 'N/A' or the budget in ones."""

	if split_budget == 'N/A':
		return split_budget
	else:
		currency, digits, units = split_budget

		# Assumes that the only possible units are millions, and if so, the 
		# string always contains the substring 'million.' This is a fair
		# assumption for now b/c we have the full dataset and that holds.
			
		if currency == u'£':

		# 	# TODO: Need to implement conversion function.
			digits = float(digits) * gbp_to_usd(year)

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

# 5. After printing each combination, it should print the average budget at the end

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
