from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import json
from sqlalchemy.orm import relationship
import random, requests, re
from kmeans import kmeans
import requests

db = SQLAlchemy()

def _all(query):
	res = []
	data = query.all()
	for row in data:
		res.append(row.toJSON())
	return res

def doMagic(js, token):
	tracklist = []
	for t in js['items']:
		s = {}
		s['id'] = t['track']['id']
		s['title'] = t['track']['name']
		s['artist'] = t['track']['artists'][0]['name']
		tracklist.append(s)
	return magic(tracklist, token)

def magic(tracklist, token):
	# bigLyric = ''
	songs = []
	for s in tracklist:
		r = requests.get("https://api.spotify.com/v1/audio-features/" + s['id'],headers={"Authorization":"Bearer " + token})
		lyrics = getLyrics(s['title'], s['artist'])
		# bigLyric = bigLyric + ' ' + lyrics
		bigLyric = [lyrics, r.json()]
		songs.append(bigLyric)
	muvies = {}
	moods = {}
	if len(lyrics) > 0:
		muvies, moods = getMuvies(songs)
	obj = {}
	obj['movies'] = muvies
	obj['songs'] = tracklist
	obj['moods'] = moods
	return obj

def getLyrics(trackname, artist):
	values={'q_track': trackname,'q_artist':artist, 'apikey':'851a954af52f9f0406ddd7f747bb0c68'}
	response = requests.get('http://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=values)
	if response.json()['message']['header']['status_code'] is not 200:
		return ''
	r = response.json()['message']['body']['lyrics']['lyrics_body']
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
