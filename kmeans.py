from sklearn.cluster import KMeans
from pandas import read_csv
import numpy as np
import json

def trainmodel(data):
    #Fit the model on the data
    kmeans = KMeans(n_clusters=50, random_state=0).fit(data)
    #Assign each movie to a cluster
    indices = kmeans.predict(data) #----pythonic indices
    #Transpose by assigning each cluster its asscociated movies
    res = [[] for i in range(50)]
    for index,cluster in enumerate(indices):
        res[cluster].append(index)
    return kmeans, res

def predict(model,lyrics):
    #Give a new lyrics, predict the cluster it belongs to 
    center = model.predict(lyrics)
    return center

def kmeans():
    #Read txt File containing the movie dataset
    with open('./movie_raw.txt') as json_data:
        txt = json.load(json_data)
    with open('./movie_indices.txt') as json_data:
        movie_indices = json.load(json_data)
    #Train and predict the lyrics
    model, clusters = trainmodel(txt)
    lyrics = np.array(lyrics_raw).reshape(1,-1)
    predicted_label = predict(model,lyrics)
    #Find the indices of the movies in that cluster
    arr_movies = clusters[predicted_label[0]]
    #Computer L2 Norm and find the 5 smallest norm values
    scores = []
    for movie in arr_movies:
        scores.append(np.linalg.norm(np.array(txt[movie]) - lyrics))
    kmeans_indices = np.array(scores).argsort()[::1][:5]
    movie_ids = []
    for index in kmeans_indices:
        movie_ids.append(movie_indices[arr_movies[index]])
    return movie_ids