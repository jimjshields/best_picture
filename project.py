# -*- coding: utf-8 -*-

import requests, re
from bs4 import BeautifulSoup

"""Overall goal:  scrape the budgets of the Academy Award 
   Best Picture winners from Wikipedia."""

# 1. Your script should go the the Wikipedia page for the award

def get_url_text(url):
	"""Given a url, return the text found at that url. Assumes the encoding
	   of the response is the encoding indicated in the HTTP headers."""

	url_response = requests.get(url)
	url_text = url_response.text
	return url_text

def get_titles(url):
	url_text = get_url_text(url)
	text_soup = BeautifulSoup(url_text)
	tables = text_soup('table')
	possible_winners = tables[96]('li')
	winners = (li for li in possible_winners if re.match(r'.+\(.+\)', str(li)))
	movies = [[li.a['href'], li.a.string, re.search(r'</i>\s+\((.+)\)</li>', str(li)).group(1)] for li in winners]
	return movies

# 2. follow the link for each year’s winner

# 3. grab the budget from the box on the right of the page

def get_movie_budget(movie_url):
	text_soup = BeautifulSoup(get_url_text('http://en.wikipedia.org{0}'.format(movie_url)))
	side_table = text_soup('table')[0]('tr')
	budget_table_rows = [tr for tr in side_table if re.search(r'>Budget<', str(tr))]
	if len(budget_table_rows) > 0:
		budget = re.sub(r'\[\d+\]', '', budget_table_rows[0].td.get_text())
	else:
		budget = 'N/A'
	return budget

# 4. print out each Year-Title-Budget combination

def get_all_movie_budgets():
	movie_list = get_titles('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')
	for movie in movie_list:
		movie.append(get_movie_budget(movie[0]).encode('utf8'))
		convert_budget_to_int(movie[3])
	return movie_list

# 5. After printing each combination, it should print the average budget at the end

def split_budget_text(budget_string):
	if budget_string == 'N/A':
		print budget_string
	else:
		groups = re.match(r'(?P<currency>\D*)\s?(?P<digits>[\d,\,]*)\s?(?P<units>\D*)', budget_string)
		if groups:
			currency = groups.group('currency')
			digits = groups.group('digits')
			units = groups.group('units')
			return (currency, digits, units)
			# print 'Cur: {0}, Digits: {1}, Units: {2}'.format(currency, digits, units)

def convert_budget_to_int(split_budget):

def get_average_budget():
	movie_list = get_all_movie_budgets()
	return reduce(lambda x: x + int(y[3]), movie_list, 0)

# print get_average_budget()

"""If you encounter any edge cases, feel free to use your best judgement 
and add a comment with your conclusion. This code should be written to 
production standards.

You can use any language you want, but there is a strong preference for a 
language where we will be able to reproduce your results (any modern, 
semi-popular language will be fine). Please add instructions about any 
additional libraries that may be necessary along with versions."""
