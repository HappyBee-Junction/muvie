from flask import Flask, render_template, request, redirect
from flask_restful import Api, reqparse, Resource
from resources import movies
import requests
import json
from model import db, doMagic

app = Flask(__name__)
api = Api(app)

client_id = '6c6b5e99bc36413682d8a803febe776f'
client_secret = '1538b0509aba4c20ab55bf758d5e9e65'

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/callback")
def movie():

	p ={'code': request.args['code'],
		'grant_type': 'authorization_code',
		'redirect_uri': 'http://localhost:8080/callback',
		'client_id': client_id,
		'client_secret': client_secret,
		'scope': 'user-read-private user-read-email user-read-recently-played'
	}
	r = requests.post('https://accounts.spotify.com/api/token', data=p, json=True)

	resp = r.json()
	limit = 10
	h ={'Authorization': 'Bearer ' + resp['access_token'],
		'scope': 'user-read-private user-read-email user-read-recently-played'
	}
	r = requests.get('https://api.spotify.com/v1/me/player/recently-played?limit=' + str(limit), headers=h, json=True)
	muvies = doMagic(r.json())
	return render_template('movie.html', movies=muvies)

class spotify(Resource):
	def get(self):
		username = 'r.benson'
		scope = 'user-read-private user-read-email user-read-recently-played'
		p = {
			'client_id': client_id,
			'client_secret': client_secret,
			'redirect_uri': 'http://localhost:8080/callback',
			'show_dialog': True,
			'response_type': 'code',
			'scope': 'user-read-private user-read-email user-read-recently-played'
		}
		r = requests.get('https://accounts.spotify.com/authorize', params=p)
		print(r)
		r.headers['Access-Control-Allow-Origin'] = '*'
		return redirect(r.url, code=302)


api.add_resource(spotify, '/spotify', endpoint='spotify')

if __name__ == '__main__':
	app.run(debug=True)