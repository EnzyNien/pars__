from bs4 import BeautifulSoup
import requests
import html5lib
import json
import re
from dateutil import parser

class pars_cls():
	#_iframe_links - linls of quest name
	#table_link - links of quest type
	def returnTime(self,time):
		time = time.get_text().replace('\t','').replace('\n','')
		time_class = parser.parse(time)
		return time_class.strftime("%H:%M")



	def getFreeandBusyDays(self, link):
		
		_table_html = requests.get(link)   
		_table_bs = BeautifulSoup(_table_html.text, "html5lib")
		_table_gridDays = _table_bs.find('',{'class':'gridDays'})	
		_table_gridDay = _table_gridDays.find_all('',{'class':self.p_gridDay})
		returt_dict = {}
		for column in _table_gridDay:
			free_time_arr = []
			busy_time_arr = []
			day_class = parser.parse(column.find('',{'class':'gridHeaderDate'})['data-content'])
			day = day_class.strftime("%Y-%m-%y")
			free_time = column.find_all('',{'class':self.p_gridFree})
			free_time_arr = [self.returnTime(i) for i in free_time]
			busy_time = column.find_all('',{'class':self.p_gridBusy})
			busy_time_arr = [self.returnTime(i) for i in busy_time]
			returt_dict.update({day:[{'free':free_time_arr},{'busy':busy_time_arr}]})
		return returt_dict


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
				_day_table = self.iframe_url+childrens[0]['href']
				_day_table_dict = self.getFreeandBusyDays(_day_table)
				table_link.append({'link_data':{link:_day_table},'time_date':_day_table_dict})

		with open('result.txt','w') as res:
			json.dump(table_link,res)

	def __init__(self):
		self.glob_url = 'https://www.roomofriddles.com/book-now'
		self.iframe_url = 'https://classic.youcanbook.me'
		self.p_gridDay= re.compile(r'gridDay(.*)')
		self.p_gridFree= re.compile(r'(.*)gridFree(.*)')
		self.p_gridBusy= re.compile(r'(.*)gridBusy(.*)')
		self.parsing()

if __name__ == '__main__':
	pars_cls = pars_cls()
