from flask import request
import datetime as dt
from flask_restful import Resource, reqparse
from model import db, Movie, _all
from sqlalchemy.sql.functions import func
import requests

class movies(Resource):
	def get(self):
		print(type(self))

		movie = (db.session.query(Movie))
		print(_all(movie))
		return(_all(movie))


	def post(self):
		return 'ok'