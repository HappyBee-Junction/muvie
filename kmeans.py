from sklearn.cluster import KMeans
from pandas import read_csv
from scipy import stats
import numpy as np
import json, requests, collections
import build, senticnet4
from senticnet.senticnet import Senticnet

alphDict = {'admiration': 0, 'anger': 0, 'disgust': 0, 'fear': 0, 'interest': 0 , 'joy': 0, 'sadness': 0, 'surprise': 0}

#Read txt File containing the dataset
with open('./movie_raw.txt') as json_data:
    txt = json.load(json_data)
with open('./movie_indices.txt') as json_data:
    movie_indices = json.load(json_data)
with open('./stopwords.txt') as json_data:
    STOPWORDS = json.load(json_data)

#Fit the model on the data
kmeans = KMeans(n_clusters=50, random_state=0).fit(txt)
#Assign each movie to a cluster
indices = kmeans.predict(txt)  # ----pythonic indices
#Transpose by assigning each cluster its asscociated movies
res = [[] for i in range(50)]
for index, cluster in enumerate(indices):
    res[cluster].append(index)

def processLyrics(lyrics):
    dic = build.builddictionary()
    sn = Senticnet()
    emotions = []
    for word in lyrics:
        if word not in STOPWORDS and word in senticnet4.senticnet:
            emotion = sn.moodtags(word)
            for emo in emotion:
                emotions.append(emo.replace("#", ""))
    #sortedList = sorted(stats.itemfreq(emotions), key=getCount)
    emoLycList = stats.itemfreq(emotions)
    emoLycDict = alphDict.copy()

    for elt in emoLycList:
        emoLycDict[elt[0]] = elt[1]
    dicLyc = collections.OrderedDict(sorted(emoLycDict.items()))

    #Compute list of frequencies out of dictionnary
    orderedEmoLycList = []
    for key in dicLyc.keys():
        orderedEmoLycList.append(int(dicLyc[key]))
    if np.linalg.norm(orderedEmoLycList) != 0.0:
        final_emotions = orderedEmoLycList / np.linalg.norm(orderedEmoLycList)
    #normalized(sortedList[::-1][:5]) #append keywords
    return final_emotions

def predict(model, lyrics):
    #Give a new lyrics, predict the cluster it belongs to
    center = model.predict(lyrics)
    return center

def kmeans(lyrics):
    lyrics_emotions = processLyrics(lyrics)
    lyrics = np.array(lyrics_emotions).reshape(1, -1)
    predicted_label = predict(model, lyrics)
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