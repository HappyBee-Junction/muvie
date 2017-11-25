from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import json
from sqlalchemy.orm import relationship
import random, requests, re
from kmeans import kmeans
# import azlyrics

db = SQLAlchemy()

def _all(query):
	res = []
	data = query.all()
	for row in data:
		res.append(row.toJSON())
	return res

def doMagic(js):
	tracklist = []
	for t in js['items']:
		s = {}
		s['title'] = t['track']['name']
		s['artist'] = t['track']['artists'][0]['name']
		tracklist.append(s)
	return magic(tracklist)

def magic(tracklist):
	bigLyric = ''
	songs = []
	for s in tracklist:
		lyrics = getLyrics(s['title'], s['artist'])
		bigLyric = bigLyric + ' ' + lyrics
	muvies = {}
	moods = {}
	if len(lyrics) > 0:
		muvies, moods = getMuvies(lyrics)
	obj = {}
	obj['movies'] = muvies
	obj['songs'] = s
	obj['moods'] = moods
	return obj

def getLyrics(trackname, artist):
	# az = azlyrics.Azlyrics(artist, trackname)
	# az.artist = artist
	# az.music = trackname
	values={'q_track': trackname,'q_artist':artist, 'apikey':'a861047a0eb1272708e4d518bee92a6d'}
	response = requests.get('http://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=values)
	if response.json()['message']['header']['status_code'] is not 200:
		return ''
	r = response.json()['message']['body']['lyrics']['lyrics_body']
	# lyrics  = az.get_lyrics()
	# lyrics = str(lyrics).replace('\\n', ' ')
	# lyrics = re.sub(r'[^\w]', ' ', lyrics)
	regex= re.compile('[^a-zA-Z]')
	r = regex.sub(' ', r[0:len(r)-74])
	return r

class Movie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)

	def __init__(self, title):
		self.title = title

	def toJSON(self):
		return ({'title': self.title, 
				})

def getMuvies(text):

	muvieList = []

	res, moods = kmeans(text)

	for m in res:
		movie = db.session.query(Movie).filter_by(id = m).first()


		values={'t':movie.title, 'apikey':'33020a1'}
		response = requests.get('http://www.omdbapi.com/', params=values)

		muvieList.append(response.json())

	return muvieList, moods
