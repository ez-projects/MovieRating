import http.client
import json

conn = http.client.HTTPSConnection("api.themoviedb.org")

payload = '{}'
api_key = 'c73d7f19c33a3c43d4f4f66a80cde8d7'
year=2017
query=f'mother'

conn.request(
	"GET", 
	f"/3/search/movie?include_adult=false&page=1&language=en&api_key={api_key}&query={query}&year={year}&primary_release_year={year}", payload)

res = conn.getresponse()
total_pages = json.loads(res.read()).get('total_pages', None)



results = {}
for page in range(total_pages):
	conn.request(
	"GET", 
	f"/3/search/movie?include_adult=false&page={page+1}&language=en&api_key={api_key}&query={query}&year={year}&primary_release_year={year}", payload)

	res = conn.getresponse()
	res_data = json.loads(res.read()).get('results', None)
	for i in res_data:
		if i.get('title', None).startswith(query.title()) and i.get('original_language', None)=='en'\
		and i.get('release_date', None).startswith(str(year)):
			if not i.get('id', None) in results.keys():
				results.update({i['id']: i})

import ipdb;ipdb.set_trace()			