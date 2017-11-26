import pandas as pd
import json
import re
from scipy import stats
import numpy as np
import build
import senticnet4
import collections

alphDict = {'admiration': 0, 'anger': 0, 'disgust': 0, 'fear': 0, 'interest': 0 , 'joy': 0, 'sadness': 0, 'surprise': 0}

genres_list = ['Action','Adventure','Animation','Comedy','Crime','Documentary','Drama','Family','Fantasy','History','Horror','Music','Mystery','Romance','Science Fiction','Thriller','War','Western']

def findemotion(word):
    sn = senticnet4.senticnet
    emotions = []
    for s in sn[word]:
        if '#' in s:
            emotions.append(s)
    return emotions

def processMovieData(dic):
    with open('./stopwords.txt') as json_data:
        STOPWORDS = json.load(json_data)
    emotions_matrix = pd.read_csv('emotions_template.csv', header=None)
    indices = []
    output = []
    filedata = pd.read_csv('tmdb_5000_movies.csv',skiprows=[1],encoding = "ISO-8859-1")
    for index,line in enumerate(filedata.values):
        indices.append(line[2]) #append id
        overview = re.findall(r"[\w']+", line[1])
        overview_emotions = []
        for o in overview:
            if o not in STOPWORDS and o in senticnet4.senticnet:
                emotion = findemotion(o)
                for emo in emotion:
                    overview_emotions.append(emo.replace("#",""))
        jsonobj = json.loads(line[0])
        keywords_emotions = []
        for obj in jsonobj:
            keyword = re.findall(r"[\w']+", obj['name'].replace("'"," ")) 
            for word in keyword:
                if word not in STOPWORDS and word in senticnet4.senticnet:
                    emotion = findemotion(word)
                    for emo in emotion:
                        keywords_emotions.append(emo.replace("#",""))
        jsonobj = json.loads(line[3].replace("\xa0",""))
        genres = []
        for obj in jsonobj:
            if obj['name'] in genres_list:
                genres.append(obj['name'])
        #Retrieve ordered dictionnary of emotions with their frequencies: dic 
        emoList = stats.itemfreq(overview_emotions + keywords_emotions)
        emoDict = alphDict.copy()
        for elt in emoList:
            emoDict[elt[0]] = elt[1]
        dic = collections.OrderedDict(sorted(emoDict.items()))
        #Compute list of frequencies out of dictionnary
        orderedEmoList = []
        for key in dic.keys():
            orderedEmoList.append(int(dic[key]))
        weighted_emotion = []
        weights = emotions_matrix.values[genres_list.index(genres[0])]
        for index,item in enumerate(orderedEmoList):
            weighted_emotion.append(item * weights[index])
        if np.linalg.norm(weighted_emotion) != 0.0:
            normEmoList = weighted_emotion / np.linalg.norm(weighted_emotion)
        
        #append keywords normalized L2 values
        output.append(normEmoList.tolist())
    with open('./movie_raw.txt', 'w') as outfile:
        json.dump(output, outfile)
    with open('./movie_indices.txt', 'w') as outfile:
        json.dump(indices, outfile)
        
if __name__=="__main__":
    processMovieData(build.builddictionary())