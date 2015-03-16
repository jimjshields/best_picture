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

def convert_html_to_bsoup(url):
	"""Given a url, gets the text at that url and attempts to convert it to
	   a BeautifulSoup object. Assumes that the text is HTML."""

	url_text = get_url_text(url)
	text_soup = BeautifulSoup(url_text)
	return text_soup

def get_titles(url):
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
		movie.append(convert_budget_to_int(split_budget_text(movie[3])))
		print movie
	return movie_list

# 5. After printing each combination, it should print the average budget at the end

def split_budget_text(budget_string):
	if budget_string == 'N/A':
		return budget_string
	else:
		groups = re.match(r'(?P<currency>\D*)\s?(?P<digits>[\d,\,,\.]*)\s?(?P<units>\D*)', budget_string)
		if groups:
			currency = groups.group('currency').strip()
			digits = groups.group('digits').replace(',', '').strip()
			units = groups.group('units').strip()
			return (currency, digits, units)

def convert_budget_to_int(split_budget):
	if split_budget == 'N/A':
		return split_budget
	else:
		currency, digits, units = split_budget
		if units == 'million':
			return float(digits) * 1000000
		else:
			return float(digits)

def get_average_budget():
	movie_list = get_all_movie_budgets()
	movies_with_budgets = filter(lambda x: x[4] != 'N/A', movie_list)
	budgets_sum = reduce(lambda x, y: x + int(y[4]), movies_with_budgets, 0)
	average_budget = budgets_sum / len(movies_with_budgets)
	return '{:0,.2f}'.format(average_budget)

print get_average_budget()

"""If you encounter any edge cases, feel free to use your best judgement 
and add a comment with your conclusion. This code should be written to 
production standards.

You can use any language you want, but there is a strong preference for a 
language where we will be able to reproduce your results (any modern, 
semi-popular language will be fine). Please add instructions about any 
additional libraries that may be necessary along with versions."""
