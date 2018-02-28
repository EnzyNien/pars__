from bs4 import BeautifulSoup
import requests
import html5lib
import json
import re
from dateutil import parser
import datetime

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
			day_class = parser.parse(column.find('',{'class':'gridHeaderDate'})['data-content']).date()
			if day_class == self.day:
				day = day_class.strftime("%d-%m-%Y")
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
		_iframe_servicenoImage = _iframe_services.find_all('',{'class':'service noImage'})
		_iframe_links = []
		for link in _iframe_servicenoImage:
			_service_description = link.find('',{'class':'serviceDescription'}).get_text()
			_serviceSelect = link.find('',{'class':'serviceSelect'})
			childrens = _serviceSelect.findChildren('a')
			_service_link = self.iframe_url + childrens[0]['href']
			_iframe_links.append([_service_description,_service_link])
			
		#parsing second page 
		table_link = []
		for link in _iframe_links:
			_team_page_html = requests.get(link[1])
			_team_page_bs = BeautifulSoup(_team_page_html.text, "html5lib")
			_team_page_teams = _team_page_bs.find('',{'class':'teams'})
			_team_noImage = _team_page_teams.find_all('',{'class':'team noImage'})
			for team in _team_noImage:
				_team_name = team.find('',{'class':'teamName'}).get_text()
				_team_description = team.find('',{'class':'teamDescription'}).get_text()
				_team_select = team.find('',{'class':'teamSelect'})
				childrens = _team_select.findChildren('a')
				_day_table = self.iframe_url+childrens[0]['href']
				_day_table_dict = self.getFreeandBusyDays(_day_table)
				table_link.append({	'service_description':link[0],
									'service_link':link[1],
									'team_name':_team_name,
									'team_description':_team_description,
									'team_link':_day_table,
									'free_busy':_day_table_dict})

		with open('result.txt','w') as res:
			json.dump(table_link,res)

	def __init__(self):
		self.glob_url = 'https://www.roomofriddles.com/book-now'
		self.iframe_url = 'https://classic.youcanbook.me'
		self.p_gridDay= re.compile(r'gridDay(.*)')
		self.p_gridFree= re.compile(r'(.*)gridFree(.*)')
		self.p_gridBusy= re.compile(r'(.*)gridBusy(.*)')
		self.day = datetime.datetime.now().date()
		self.day_str = self.day.strftime("%Y-%m-%d")
		self.parsing()

if __name__ == '__main__':
	pars_cls = pars_cls()
