from bs4 import BeautifulSoup
import requests
import html5lib
import json

class pars_cls():

	def parsing(self):
		html = requests.get(self.glob_url)
		bs = BeautifulSoup(html.text, "html5lib")

		#<input type="hidden" name="cal" value="soSoQew5iFXb2MBfr7cY
		_name = bs.find('',{'class':'main-content','id':'content'})	
		_iframe_src = _name.find('iframe')['src']
		_iframe_html = requests.get(_iframe_src)
		#iframe
		_iframe_bs = BeautifulSoup(_iframe_html.text, "html5lib")
		_iframe_services = _iframe_bs.find('',{'class':'services chooseOne'})
		_iframe_serviceSelect = _iframe_services.find_all('',{'class':'serviceSelect'})
		_iframe_links = []
		for link in _iframe_serviceSelect:
			childrens = link.findChildren('a')
			_iframe_links.append(self.iframe_url + childrens[0]['href'])
		#parsing second page 
		table_link = []
		for link in _iframe_links:
			_second_page_html = requests.get(link)
			_second_page_bs = BeautifulSoup(_second_page_html.text, "html5lib")
			_second_page_teams = _second_page_bs.find('',{'class':'teams'})
			_teams_teamSelect = _second_page_teams.find_all('',{'class':'teamSelect'})
			for teams in _teams_teamSelect:
				childrens = teams.findChildren('a')
				table_link.append({link:self.iframe_url+childrens[0]['href']})

		with open('result.txt','w') as res:
			json.dump(table_link,res)

	def __init__(self):
		self.glob_url = 'https://www.roomofriddles.com/book-now'
		self.iframe_url = 'https://classic.youcanbook.me'
		self.parsing()

if __name__ == '__main__':
	pars_cls = pars_cls()
