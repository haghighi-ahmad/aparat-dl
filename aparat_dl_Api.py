__author__ = "https://github.com/mehdigudy, https://gitlab.com/frowzyispenguin"
__license__ = "GNU3"
__version__ = "0.1"
__maintainer__ = "Mehdi"
__email__ = "thisismrmehdi@hotmail.com"


import requests
from bs4 import BeautifulSoup as bs
import os
import sys
import youtube_dl
import urllib.request


def dllink_extractor(link):
	'''
	find the best quality that available and return it
	:param str link
	:reutrn: the best quality
	:rtype: str
	'''
	resolutions = ['720p', '480p', '360p', '240p', '144p']
	src = requests.get(link)
	soup = bs(src.text, "html.parser")
	links = []
	for i in soup.find_all("a"):
		k = str(i).split("href")[1].split('"')
		for j in k:
			if j.count("http") and j.count("cdn"):
				links.append(j)
	link_list = {}
	for i in links:
		for j in resolutions:
			if i.count(j):
				link_list[j] = i
	ordered_res = list(link_list.keys())
	ordered_res.sort()
	return link_list[ordered_res[-1]]


def vlink_extractor(link):
	'''
	grab all links of all videos in playlist
	:param str link
	:return: all links of page in playlist
	:rtype: list
	'''
	src = requests.get(link)
	soup = bs(src.text, "html.parser")
	video_links = []
	for i in str(soup.find_all(attrs={'class': 'playlist-body'})).split('"'):
		if i.count("/v/"):
			video_links.append(i)
	links = []
	for i in range(0, len(video_links), 2):
		links.append(
			"https://aparat.com{}".format(video_links[i].split("/%")[0]))
	# links of all videos in playlist
	links = dict.fromkeys(links).keys()
	return links


class AparatDlApi():
	'''
	 an api for download videos from aparat.com
	Methods
	-------
	singleVideo(link)
			Download Single video
	playList(link)
			Downlaod a playlist in order
	wholeChannel(link)
			Download the whole Channel
	'''
	@staticmethod
	def singleVideo(link):
		'''
		Download Single video
		:param str link
		'''
		src = requests.get(link)
		soup = bs(src.text, "html.parser")
		name = soup.title.string
		name =name.replace("\n", " ") 
		thelink = dllink_extractor(link)
		ydl_opts = {
			'outtmpl': name+".mp4",
			'retries': 999,
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			result = ydl.extract_info(
				thelink,
				download=True)

	@staticmethod
	def playList(link):
		'''
		Downlaod a playlist in order
		:param str link
		'''
		# grab the palylist name
		src = requests.get(link)
		soup = bs(src.text, "html.parser")
		atag = soup.find_all('span',  attrs={'class': 'd-in v-m'})
		atag = list(atag)
		if len(atag) == 0:
			raise Exception("This is not a play list link ")
		for i in atag:
			temp = i
		temp = list(temp)
		pdir = temp[0]
		links = vlink_extractor(link)
		l2 =list(links)
		for j in links:
			# grab name of videos
			src = requests.get(j)
			soup = bs(src.text, "html.parser")
			name = soup.title.string
			name =name.replace("\n", " ") 
			# grab links of videos
			thelink = dllink_extractor(j)
			# download videos one by one
			orderoflist = l2.index(j)
			orderoflist+=1
			fname =str(orderoflist ) + " -"+name + ".mp4"
			ydl_opts = {
				'outtmpl': pdir + "/"+fname,
				'retries': 999,
			}
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				result = ydl.extract_info(
					thelink,
					download=True)


	@staticmethod
	def selectFromPlayList(link , start=0, end=100 ):
		'''
		Download videos by selection on a playlist 
		:param str link
		:param start int 
		"param end int
		'''
		# grab the palylist name
		src = requests.get(link)
		soup = bs(src.text, "html.parser")
		atag = soup.find_all('span',  attrs={'class': 'd-in v-m'})
		atag = list(atag)
		if len(atag) == 0:
			raise Exception("This is not a play list link ")
		for i in atag:
			temp = i
		temp = list(temp)
		pdir = temp[0]
		links = list(vlink_extractor(link))
		links.insert(0, "test") 
		end+=1
		try:
			links2 = links[start:end]
		except Exception as E :
			raise E
		for i in range (start , end):
			src = requests.get(links[i])
			soup = bs(src.text, "html.parser")
			name = soup.title.string
			name =name.replace("\n", " ") 
			# grab links of videos
			thelink = dllink_extractor(links[i])
			# download videos one by one
			fname = str(i) + " -" + name+".mp4"
			ydl_opts = {
				'outtmpl': pdir + "/"+fname,
				'retries': 999,
			}
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				result = ydl.extract_info(
					thelink,
					download=True)

	@staticmethod
	def fromFile(ifile):

		tlinks = []
		with open(ifile) as f:
			tlinks = [line.rstrip() for line in f]
		j =0 
		for i in tlinks:
			src = requests.get(i)
			soup = bs(src.text, "html.parser")
			name = str(j)+ " - "+soup.title.string
			name =name.replace("\n", " ") 
			thelink = dllink_extractor(i)
			ydl_opts = {
				'outtmpl': name+".mp4",
				'retries': 999,
			}
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				result = ydl.extract_info(
					thelink,
					download=True)
			j+=1

	@staticmethod
	def wholeChannel(link):
		'''
		Download  whole Channel
		:param str link
		'''
		# FIXME:aparat pages are dynamic and need to use Seleniumtolibrary get the whole videos
		web = link
		req = urllib.request.Request(web, data=None, headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		})
		page = urllib.request.urlopen(req)
		ReadingThePage = page.read().decode('utf-8')
		soup = bs(ReadingThePage,  features="lxml")
		atag = soup.findAll('span', attrs={'class': 'name'})
		atag = str(atag)
		atag = atag[20:]
		thefolder = atag[:-8]
		if thefolder == "" or thefolder == "/":
			raise Exception("This is a playlist link ! ")
		atag = soup.findAll('a', attrs={'class': 'thumb thumb-preview'})
		links = []
		for i in atag:
			links.append(i["href"])
		for j in links:
			link = "https://aparat.com" + j
			src = requests.get(link)
			soup = bs(src.text, "html.parser")
			name = soup.title.string
			name1 =name.replace("\n", " ") 
			name2 = name1.replace("/", " ")
			thelink = dllink_extractor(link)
			ydl_opts = {
				'outtmpl': f"{thefolder}/{name2}" + ".mp4",
				'retries': 999,
			}
			with youtube_dl.YoutubeDL(ydl_opts) as ydl:
				result = ydl.extract_info(
					thelink,
					download=True)


# when its run from terminal or cmd
if __name__ == "__main__":
	ap = AparatDlApi()
	arg = sys.argv[:]
	try:
		if arg.count("-H") or arg.count("--help"):
			print(
				'''
			Options:
				-H , --help : Helps you =)
				-A , --allvideos  : Download whole Channel
						aparat_dl -A [link]
				-L , --playlist : Download whole playlist
						aparat_dl -L [link]
				-SL, --selectfromlist: Download videos by selection on a playlist  
						aparat_dl  -SL [startpoint] [endpoint] [link]
				-F , --FromFile: grabs links from a txt file 
						aprat_dl -F path/to/txt/file


			'''
			)
		elif len(arg) == 1:
			print("""
			There is no link
			Use help -H or --help to see how scripts work
			aparat_dl.py [argumans][link]
			or
			aparat_dl [argumans][link]
			""")

		elif len(arg) == 2 and arg[-1].count("http") or len(arg) == 2 and arg[-1].count("https"):
			try:
				ap.singleVideo(arg[-1])
			except:
				pass

		elif len(arg)==3 and arg.count("-F") or len(arg) == 3 and arg.count("--FromFile") :
			if arg[-1].count(".txt") :
				try:
					ap.fromFile(arg[-1])
				except Exception as identifier:
					print("Excepiton from here: " + str(identifier))

		elif len(arg) == 3 and arg.count("-L") or len(arg) == 3 and arg.count("--playlist"):
			if arg[-1].count("https://") or arg[-1].count("http://"):
				try:
					ap.playList(arg[-1])
				except Exception as identifier:
					print("Excepiton : " + str(identifier))

		elif len(arg) == 3 and arg.count("-A") or len(arg) == 3 and arg.count("--allvideos"):
			if arg[-1].count("https://") or arg[-1].count("http://"):
				try:
					ap.wholeChannel(arg[-1])
				except Exception as identifier:
					print("Excepiton : " + str(identifier))

		elif len(arg) == 5 and arg.count("-SL") or len(arg) == 5 and arg.count("--selectfromlist"):
			if arg[-1].count("https://") or arg[-1].count("http://"):
				try:
					ap.selectFromPlayList(arg[-1] , int(arg[-3]) ,int(arg[-2]))
				except Exception as identifier:
					print("Excepiton : " + str(identifier))                    
		else:
			print(  """
			Use help -H or --help to see how scripts work
			python -m  aparat_dl.py [argumans][link]
			or 
			aparat_dl [argumans][link]
			""")
	except KeyboardInterrupt as e:
		print ("\n you just killed the program mate ! ")
		sys.exit()

	except Exception as e:
		print(str(e))
