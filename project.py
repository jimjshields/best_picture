# -*- coding: utf-8 -*-

import requests
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
	rows = text_soup('table')
	print rows

get_titles('http://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture')

# 2. follow the link for each year’s winner

# 3. grab the budget from the box on the right of the page

# 4. print out each Year-Title-Budget combination

# 5. After printing each combination, it should print the average budget at the end


"""If you encounter any edge cases, feel free to use your best judgement 
and add a comment with your conclusion. This code should be written to 
production standards.

You can use any language you want, but there is a strong preference for a 
language where we will be able to reproduce your results (any modern, 
semi-popular language will be fine). Please add instructions about any 
additional libraries that may be necessary along with versions."""
