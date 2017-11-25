from flask_sqlalchemy import SQLAlchemy
import datetime as dt
import json
from sqlalchemy.orm import relationship
import random, requests, re

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
	res = []
	for s in tracklist:

		lyrics = getLyrics(s['title'], s['artist'])
		if len(lyrics) > 0:
			muvies = getMuvies(lyrics)
			res = res + muvies
	return res

def getLyrics(trackname, artist):
	values={'q_track': trackname,'q_artist':artist, 'apikey':'a861047a0eb1272708e4d518bee92a6d'}

	response = requests.get('http://api.musixmatch.com/ws/1.1/matcher.lyrics.get', params=values)

	if response.json()['message']['header']['status_code'] is not 200:
		return ''
	r=response.json()['message']['body']['lyrics']['lyrics_body']

	regex= re.compile('[^a-zA-Z]')
	r = regex.sub(' ', r[0:len(r)-74])
	return (r)

def getMuvies(text):
	json_muvies =[
		{'Director': 'Abel Ferrara', 'Genre': 'Action, Drama, Thriller', 'imdbVotes': '451', 'imdbID': 'tt0091121', 'Metascore': 'N/A', 'Writer': 'William Bleich (television story and teleplay), Tom Schulman (story), Jeffrey Walker (story)', 'Response': 'True', 'BoxOffice': 'N/A', 'Runtime': '98 min', 'Website': 'N/A', 'Awards': 'N/A', 'Title': 'The Gladiator', 'Actors': 'Ken Wahl, Nancy Allen, Robert Culp, Stan Shaw', 'Production': 'New World Television', 'Ratings': [{'Source': 'Internet Movie Database', 'Value': '5.5/10'}], 'Country': 'USA', 'Released': '03 Feb 1986', 'Rated': 'NOT RATED', 'imdbRating': '5.5', 'Plot': "A road warrior vigilante avenges his brother's death at the hands of a crazy motorist by using his souped-up pickup to apprehend drunken drivers and others who abuse their driving privileges.", 'Language': 'English', 'Poster': 'https://images-na.ssl-images-amazon.com/images/M/MV5BMTUyMzgwMDg5MV5BMl5BanBnXkFtZTcwMTcxNjcyMQ@@._V1_SX300.jpg', 'Year': '1986', 'DVD': '01 Mar 2005', 'Type': 'movie'},
		{'imdbID': 'tt0298130', 'Plot': 'A journalist must investigate a mysterious videotape which seems to cause the death of anyone in a week of viewing it.', 'BoxOffice': '$128,579,698', 'Awards': '14 wins & 11 nominations.', 'Year': '2002', 'imdbRating': '7.1', 'Genre': 'Horror, Mystery', 'Production': 'DreamWorks SKG', 'Title': 'The Ring', 'Released': '18 Oct 2002', 'Actors': 'Naomi Watts, Martin Henderson, David Dorfman, Brian Cox', 'Ratings': [{'Value': '7.1/10', 'Source': 'Internet Movie Database'}, {'Value': '72%', 'Source': 'Rotten Tomatoes'}, {'Value': '57/100', 'Source': 'Metacritic'}], 'Country': 'USA, Japan', 'imdbVotes': '277,934', 'Runtime': '115 min', 'Rated': 'PG-13', 'Director': 'Gore Verbinski', 'Type': 'movie', 'DVD': '04 Mar 2003', 'Poster': 'https://images-na.ssl-images-amazon.com/images/M/MV5BNDA2NTg2NjE4Ml5BMl5BanBnXkFtZTYwMjYxMDg5._V1_SX300.jpg', 'Language': 'English', 'Response': 'True', 'Website': 'http://www.ring-themovie.com', 'Metascore': '57', 'Writer': 'Ehren Kruger (screenplay), Kôji Suzuki (novel)'},
		{'Director': 'Peter Jackson', 'BoxOffice': '$339,700,000', 'Runtime': '179 min', 'Country': 'USA, New Zealand', 'Actors': 'Bruce Allpress, Sean Astin, John Bach, Sala Baker', 'imdbID': 'tt0167261', 'Poster': 'https://images-na.ssl-images-amazon.com/images/M/MV5BMDY0NmI4ZjctN2VhZS00YzExLTkyZGItMTJhOTU5NTg4MDU4XkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg', 'Title': 'The Lord of the Rings: The Two Towers', 'Website': 'http://www.lordoftherings.net/', 'Production': 'New Line Cinema', 'Language': 'English, Sindarin, Old English', 'Year': '2002', 'Writer': 'J.R.R. Tolkien (novel), Fran Walsh (screenplay), Philippa Boyens (screenplay), Stephen Sinclair (screenplay), Peter Jackson (screenplay)', 'DVD': '26 Aug 2003', 'Released': '18 Dec 2002', 'Rated': 'PG-13', 'Awards': 'Won 2 Oscars. Another 118 wins & 138 nominations.', 'Metascore': '88', 'Genre': 'Adventure, Drama, Fantasy', 'Type': 'movie', 'Response': 'True', 'imdbVotes': '1,213,608', 'Plot': "While Frodo and Sam edge closer to Mordor with the help of the shifty Gollum, the divided fellowship makes a stand against Sauron's new ally, Saruman, and his hordes of Isengard.", 'imdbRating': '8.7', 'Ratings': [{'Value': '8.7/10', 'Source': 'Internet Movie Database'}, {'Value': '96%', 'Source': 'Rotten Tomatoes'}, {'Value': '88/100', 'Source': 'Metacritic'}]}
	]
	muvies = []
	for muvie in json_muvies:
		m = Movie(muvie['Title'], muvie['Poster'])
		muvies.append(m.toJSON())
	return json_muvies


class Movie(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	poster = db.Column(db.String)
	happy = db.Column(db.Float)
	sad = db.Column(db.Float)
	epic = db.Column(db.Float)

	def __init__(self, title, poster, moods=None):
		self.title = title
		self.poster = poster
		# self.happy = happy
		# self.sad = sad
		# self.epic = epic

	def toJSON(self):
		return ({'title': self.title, 
				'poster': self.poster,
				})
