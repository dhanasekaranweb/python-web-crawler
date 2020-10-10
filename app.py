from urllib.request import urlopen
from bs4 import BeautifulSoup
from newspaper import Article
import json
import sys, re


class WebCrawler:
	def __init__(self,url):
		self.url = url
		self.is_downloaded = False
		self.content = ""

		#structured the data
		self.structured_data = {
			"website_link": self.url,
			"links": [],
			"content":"",
			"content_html":"",
			"content_keywords":"",
			"summary":"",
			"meta_title":"",
			"meta_keywords":"",
			"meta_description":"",
			"top_image":"",
			"authors":"",
			"publish_date":""
		}

		self.init_crawl()

	def init_crawl(self):
		self.is_downloaded = self.initDownloadContent()
		if(self.is_downloaded):
			self.parseDate()
		else:
			raise ValueError("Something went wrong in URL")

	def initDownloadContent(self):
		try:
			html = urlopen(self.url)
			self.content = html
			return True

		except:
			return False

	def parseDate(self):
		soup = BeautifulSoup(self.content,'lxml')

		#read the title tag
		title = soup.title
		self.structured_data["meta_title"] = title.getText() or ""

		#read href links and texts
		for singleText in soup.find_all('a'):
			self.structured_data["links"].append({
				"link_text":BeautifulSoup(str(singleText), 'lxml').getText(),
				"link_href":singleText.get("href"),
				"link_alt":singleText.get("alt")
				})

		#read meta desc and keyword
		for meta in soup.findAll("meta"):
			metaname = meta.get('name', '').lower()
			metaprop = meta.get('property', '').lower()
			if 'description' == metaname or metaprop.find("description")>0:
				self.structured_data["meta_description"] = meta['content'].strip()
			if 'keywords' == metaname or metaprop.find("keywords")>0:
				self.structured_data["meta_keywords"] = meta['content'].strip()

		#read the content
		self.parseContent()

	def parseContent(self):
		article = Article(self.url)
		article.download()
		article.parse()
		article.nlp() 
		self.structured_data["summary"] = article.summary
		self.structured_data["content"] = article.text
		self.structured_data["content_html"] = article.article_html
		self.structured_data["top_image"] = article.top_image
		self.structured_data["authors"] = article.authors
		self.structured_data["publish_date"] = article.publish_date

	def getJSON(self):
		if(self.is_downloaded):
			return json.dumps(self.structured_data,indent=4, sort_keys=True)
		else:
			return json.dumps({"error":"Invalid URL / Download Failed"})


# Validated URL
def validateURL(url):
	regex = re.compile(
		r'^(?:http|ftp)s?://' # http:// or https://
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
		r'localhost|' #localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
		r'(?::\d+)?' # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	return re.match(regex, url) is not None  

# SampleCode Objects
if(len(sys.argv) == 2):
	url= sys.argv[1]
	if(url): 
		if(validateURL(url)):   
			crawl = WebCrawler(url)
			data = crawl.getJSON()
			print(data)
		else:
		   print("URL Invalid")
	else:
		   print("URL Parameter missing!")
