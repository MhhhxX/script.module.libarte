# -*- coding: utf-8 -*-
import json
import libmediathek3 as libMediathek
import re
import urllib
import xbmc
import datetime
import time
from operator import itemgetter
#import xml.etree.ElementTree as ET

langs = ['de', 'fr']

setting = libMediathek.getSetting
language = langs[int(setting("lang"))]

xbmc.log(language, xbmc.LOGNOTICE)

opa_token = {"Authorization": "Bearer Nzc1Yjc1ZjJkYjk1NWFhN2I2MWEwMmRlMzAzNjI5NmU3NWU3ODg4ODJjOWMxNTMxYzEzZGRjYjg2ZGE4MmIwOA"}
emac_token = {"Authorization": "Bearer MWZmZjk5NjE1ODgxM2E0MTI2NzY4MzQ5MTZkOWVkYTA1M2U4YjM3NDM2MjEwMDllODRhMjIzZjQwNjBiNGYxYw"}

opa_url = 'https://api.arte.tv/api/opa/v3/'
	
def getVideos(url):
	l = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	for video in j['videos']:
		d = {}
		#d['_name'] = video['title']
		if video['subtitle'] != None:
			d['_name'] = video['subtitle']
		else:
			d['_name'] = video['title']
		
		d['_tvshowtitle'] = video['title']
		if video['imageUrl'] != None:
			d['_thumb'] = video['imageUrl']
		if video['durationSeconds'] != None:
			d['_duration'] = str(video['durationSeconds'])
		if video['teaserText'] != None:
			d['_plotoutline'] = video['teaserText']
			d['_plot'] = video['teaserText']
		if video['fullDescription'] != None:
			d['_plot'] = video['fullDescription']
		elif video['shortDescription'] != None:
			d['_plot'] = video['shortDescription']
		#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+video['programId']+'/'+video['kind']+'/'+video['platform']+'/de/DE'
		d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+video['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
		d['mode'] = 'libArtePlay'
		d['_type'] = 'date'
		l.append(d)
	if j['meta']['page'] < j['meta']['pages']:
		d = {}
		d['url'] = url.split('&page=')[0] + '&page=' + str(j['meta']['page'] + 1)
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l

def getAZ():
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/home/de')
	j = json.loads(response)
	for mag in j['teasers']['magazines']:
		d = {}
		d['_name'] = mag['label']['de']
		d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/' + mag['url'] + '/de'
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l
	
def getPlaylists():#,playlists, highlights
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/EMAC/teasers/home/de')
	j = json.loads(response)
	for playlist in j['teasers']['playlists']:
		d = {}
		d['_name'] = playlist['title']
		d['_subtitle'] = playlist['subtitle']
		d['_thumb'] = playlist['imageUrl']
		d['_plot'] = playlist['teaserText']
		d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/PLAYLIST/' + playlist['programId'] + '/de'
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideos'
		l.append(d)
	return l
		
	
	
def getDate(yyyymmdd):
	l = []
	response = libMediathek.getUrl('http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/programs/'+yyyymmdd+'/de')
	j = json.loads(response)
	for program in j['programs']:
		if program['video'] != None:
			d = {}
			#d['_airedtime'] = program['broadcast']['broadcastBeginRounded'].split(' ')[-2][:5]
			s = program['broadcast']['broadcastBeginRounded'].split(' ')[-2].split(':')
			d['_airedtime'] = str(int(s[0]) + 1) + ':' + s[1]
			if len(d['_airedtime']) == 4:
				d['_airedtime'] = '0' + d['_airedtime']
			d['_name'] = program['program']['title']
			#d['url'] = 'http://www.arte.tv/papi/tvguide/videos/stream/player/D/'+program['video']['emNumber']+'_PLUS7-D/ALL/ALL.json'
			#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/SHOW/ARTEPLUS7/de/DE'
			#d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/streams/'+program['video']['programId']+'/'+program['video']['kind']+'/'+program['video']['platform']+'/de/DE'
			
			d['url'] = 'https://api.arte.tv/api/player/v1/config/de/'+program['video']['programId']+'?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
			#d['programId'] = program['video']['programId']
			
			if program['video']['imageUrl'] != None:
				d['_thumb'] = program['video']['imageUrl']
			if program['video']['durationSeconds'] != None:
				d['_duration'] = str(program['video']['durationSeconds'])
			if program['video']['teaserText'] != None:
				d['_plotoutline'] = program['video']['teaserText']
				d['_plot'] = program['video']['teaserText']
			if program['video']['fullDescription'] != None:
				d['_plot'] = program['video']['fullDescription']
			d['mode'] = 'libArtePlay'
			d['_type'] = 'date'
			l.append(d)
	return l

def getSearch(s):
	l = []
	url = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/search/text/'+urllib.quote_plus(s)+'/de'
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	for video in j['teasers']:
		d = {}
		d['_name'] = video['title']
		
		d['_tvshowtitle'] = video['title']
		if video['imageUrl'] != None:
			d['_thumb'] = video['imageUrl']
		d['_plot'] = video['shortDescription']
		if video['kind'] == 'SHOW' or video['kind'] == 'BONUS':
			d['_duration'] = str(float(video['duration']) * 60)
			d['url'] = 'https://api.arte.tv/api/player/v1/config/de/' + video[
				'programId'] + '?autostart=0&lifeCycle=1&lang=de_DE&config=arte_tvguide'
			d['mode'] = 'libArtePlay'
			d['_type'] = 'date'
		else:
			d['url'] = 'http://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/videos/collection/PLAYLIST/' + video[
				'programId'] + '/de'
			d['mode'] = 'libArteListVideos'
			d['_type'] = 'dir'
		l.append(d)
	return l


def getCategories():
	l = []
	response = libMediathek.getUrl(opa_url + 'categories?language=' + language, headers=opa_token)
	j = json.loads(response)
	for category in j['categories']:
		d = {}
		d['_name'] = category['label']
		d['_plot'] = category['description']
		d['mode'] = 'libArteSubcategories'
		d['_type'] = 'dir'
		d['subcategories'] = json.dumps(category['subcategories'])
		l.append(d)
	return l


def getSubcategories(sublist):
	l = []
	subcategories = json.loads(sublist)
	for subcategory in subcategories:
		d = {}
		d['_name'] = subcategory['label']
		d['_plot'] = subcategory['description']
		d['url'] = opa_url + '/videos?sort=broadcastBegin&language=' + language + '&subcategory.code=' + subcategory['code']
		d['_type'] = 'dir'
		d['mode'] = 'libArteListVideosNew'
		l.append(d)
	return l


def getListings(url, audio_desc=''):
	l = []
	response = libMediathek.getUrl(url, headers=emac_token)
	j = json.loads(response)
	for video in j['data']:
		d = {}
		d['_name'] = video['title']
		d['_plot'] = video['description']
		d['_type'] = 'date'
		if video['images']['landscape']:
			max_res = max(video['images']['landscape']['resolutions'], key=lambda item: item['w'])
			d['_thumb'] = max_res['url']
		elif video['images']['portrait']:
			max_res = max(video['images']['portrait']['resolutions'], key=lambda item: item['h'])
			d['_thumb'] = max_res['url']
		d['_duration'] = video['duration']
		d['url'] = opa_url + '/videoStreams?programId=' + video['programId'] + '&mediaType=hls&language=' + language
		d['mode'] = 'libArtePlayNew'
		d['audioDesc'] = audio_desc
		l.append(d)
	if j['nextPage']:
		d = {}
		d['url'] = j['nextPage']
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListListings'
		if bool(audio_desc):
			d['audioDesc'] = 'True'
		l.append(d)
	return l


def getVideosNeu(url):
	l = []
	response = libMediathek.getUrl(url, headers=opa_token)
	j = json.loads(response)
	for video in j['videos']:
		d = {}
		if video['subtitle'] != None and video['title'] != None:
			d['_name'] = video['subtitle'] + ' | ' + video['title']
		elif video['subtitle'] != None:
			d['_name'] = video['subtitle']
		else:
			d['_name'] = video['title']

		d['_tvshowtitle'] = video['title']
		if video['mainImage']['url'] != None:
			d['_thumb'] = video['mainImage']['url']
		if video['durationSeconds'] != None:
			d['_duration'] = str(video['durationSeconds'])
		if video['teaserText'] != None:
			d['_plotoutline'] = video['teaserText']
			d['_plot'] = video['teaserText']
		if video['fullDescription'] != None:
			d['_plot'] = video['fullDescription']
		elif video['shortDescription'] != None:
			d['_plot'] = video['shortDescription']
		d['url'] = video['links']['videoStreams']['href'] + '&mediaType=hls&language=' + language
		d['mode'] = 'libArtePlayNew'
		d['_type'] = 'date'
		l.append(d)
	if j['meta']['videos']['page'] < j['meta']['videos']['pages']:
		d = {}
		d['url'] = j['meta']['videos']['links']['next']['href']
		d['_type'] = 'nextPage'
		d['mode'] = 'libArteListVideosNew'
		l.append(d)
	return l

langs = {
	'de': ['VA', 'VOA'],
	'deSub': ['VOA-STA', 'VA-STA'],
	'deDesc': 'VAAUD',
	'fr': ['VF', 'VOF'],
	'frSub': ['VF-STF', 'VOF-STF'],
	'frDesc': 'VFAUD'
}


def getVideoUrlNew(url, audio_desc=''):
	response = libMediathek.getUrl(url, headers=opa_token)
	j = json.loads(response)
	d = {'media': [], 'metadata': {}}
	result = {'type': 'video', 'stream': 'HLS'}
	fallback_sub = {'type': 'video', 'stream': 'HLS'}
	fallback = {'type': 'video', 'stream': 'HLS'}
	streams = sorted(j['videoStreams'], key=lambda item: item['durationSeconds'])
	xbmc.log(json.dumps(streams), xbmc.LOGDEBUG)
	for stream in streams:
		audio_code = stream['audioCode']
		quality = stream['quality']
		xbmc.log(audio_desc, xbmc.LOGNOTICE)
		if bool(audio_desc) and audio_code == langs[language + 'Desc']:
			result['url'] = stream['url']
		if audio_code in langs[language] and not quality == 'SQ' and not 'url' in result:
			result['url'] = stream['url']
			d['metadata']['duration'] = stream['durationSeconds']
		if audio_code in langs[language + 'Sub'] and not quality == 'SQ':
			fallback_sub['url'] = stream['url']
		if not 'url' in fallback_sub and 'STA' in audio_code and not quality == 'SQ':
			fallback_sub['url'] = stream['url']
		if 'VO' in audio_code:
			fallback['url'] = stream['url']

	xbmc.log(json.dumps(result), xbmc.LOGNOTICE)
	if 'url' in result:
		d['media'].append(result)
	elif not 'url' in result and 'url' in fallback_sub:
		d['media'].append(fallback_sub)
	else:
		d['media'].append(fallback)
	return d


preferences = {
				'ignore':0,
				'FR':1,
				'OV':2,
				'OMU':3,
				'DE':4,}
	
languages = {
				'FR':'FR',
				'OMU':'DE',
				'DE':'DE'}
				
bitrates = {
				'EQ':800,
				'HQ':1500,
				'SQ':2200,}
	
#legend:
#
#VO Original Voice	
#VOA Original Voice	Allemande
#VOF Original Voice Francaise
#VA Voice Allemande
#VF Voice Francaise
#VAAUD Audio Description Allemande
#VFAUD Audio Description Francaise
#VE* Other Voice
#
#STA Subtitle Allemande
#STF Subtitle Francaise
#STE* Subtitle Other
#STMA Subtitle Mute Allemande
#STMF Subtitle Mute Francaise
#
#* is always followed by the provided language
#[ANG] English
#[ESP] Spanish
#[POL] Polish
#
#examples:
#VOF-STE[ANG] original audio (french), english subtitles
#VOA-STMA orignal audio (german), with french mute sutitles

lang = {
		'VO':'ov',
		'OmU':'ov',
		'VA':'de',
		'VF':'fr',
		'VA-STA':'de',
		'VF-STF':'fr',
		
		'VOA':'de',
		'VOF':'fr',
		'VOA-STA':'omu',
		'VOA-STE':'omu',
		'VOF-STA':'omu',
		'VOF-STE':'omu',
		'VO-STA': 'omu',
		# 'VAAUD':'de',
		# 'VFAUD':'fr',
		'VE[ANG]':'en',
		'VE[ESP]':'es',
		'VE[POL]':'pl',
		
		'STA':'de',
		'STF':'fr',
		'STMA':'de',
		'STMF':'fr',
		'STE[ANG]':'en',
		'STE[ESP]':'es',
		'STE[POL]':'pl',
}
def getVideoUrl(url):
	d = {}
	d['media'] = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	storedLang = 0
	for stream in j['videoStreams']:
		properties = {}
		properties['url'] = stream['url']
		properties['bitrate'] = bitrates[stream['quality']]
		
		s = stream['audioCode'].split('-')
		properties['lang'] = lang[s[0]]
		if s[0] == 'VAAUD' or s[0] == 'VFAUD':
			properties['audiodesc'] = True
		if len(s) > 1:
			properties['subtitlelang'] = lang[s[1]]
			if s[1] == 'STMA' or s[1] == 'STMF':
				properties['sutitlemute'] = True
		
		properties['type'] = 'video'
		properties['stream'] = 'MP4'
		d['media'].append(properties)
	return d
	
def getVideoUrlWeb(url):
	d = {}
	d['media'] = []
	response = libMediathek.getUrl(url)
	j = json.loads(response)
	#for caption in j.get('captions',[]):
	#	if caption['format'] == 'ebu-tt-d-basic-de':
	#		d['subtitle'] = [{'url':caption['uri'], 'type':'ttml', 'lang':'de', 'colour':True}]
	#	#elif caption['format'] == 'webvtt':
	#	#	d['subtitle'] = [{'url':caption['uri'], 'type':'webvtt', 'lang':'de', 'colour':False}]
	storedLang = 0
	for key in j['videoJsonPlayer']['VSR']:#oh, this is such bullshit. there are endless and senseless permutations of language/subtitle permutations. i'll have to rewrite this in the future for french and other languages, subtitles, hearing disabled, ... who the hell uses baked in subtitles in 2017?!?!
		l = lang.get(j['videoJsonPlayer']['VSR'][key]['versionCode'].split('[')[0],'ignore').upper()
		if preferences.get(l,0) > storedLang and j['videoJsonPlayer']['VSR'][key]['mediaType'] == 'hls':
			storedLang = preferences.get(l,0)
			result = {'url':j['videoJsonPlayer']['VSR'][key]['url'], 'type': 'video', 'stream':'HLS'}
	d['media'].append(result)
	
	d['metadata'] = {}
	d['metadata']['name'] = j['videoJsonPlayer']['VTI']
	if 'VDE' in j['videoJsonPlayer']:
		d['metadata']['plot'] = j['videoJsonPlayer']['VDE']
	elif 'V7T' in j['videoJsonPlayer']:
		d['metadata']['plot'] = j['videoJsonPlayer']['V7T']
	d['metadata']['thumb'] = j['videoJsonPlayer']['VTU']['IUR']
	d['metadata']['duration'] = str(j['videoJsonPlayer']['videoDurationSeconds'])
	return d