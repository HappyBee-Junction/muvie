import pandas as pd
import json
from senticnet.senticnet import Senticnet
import re
from scipy import stats
import numpy as np
import build
import senticnet4
import collections

array = ['id','genres', 'keywords','overview', 'release_date', 'runtime', 'tagline', 'title', 'vote_average']
alphDict = {'admiration': 0, 'anger': 0, 'disgust': 0, 'fear': 0, 'interest': 0 , 'joy': 0, 'sadness': 0, 'surprise': 0}

def processMovieData(dic):
    with open('./stopwords.txt') as json_data:
        STOPWORDS = json.load(json_data)
    sn = Senticnet()
    indices = []
    output = []
    filedata = pd.read_csv('tmdb_5000_movies.csv',skiprows=[1])
    for index,line in enumerate(filedata.values):
        indices.append(line[2]) #append id
        overview = re.findall(r"[\w']+", line[1])
        overview_emotions = []
        for o in overview:
            if o not in STOPWORDS and o in senticnet4.senticnet:
                emotion = sn.moodtags(o)
                for emo in emotion:
                    overview_emotions.append(emo.replace("#",""))
        jsonobj = json.loads(line[0])
        keywords_emotions = []
        for obj in jsonobj:
            keyword = re.findall(r"[\w']+", obj['name'].replace("'"," ")) 
            for word in keyword:
                if word not in STOPWORDS and word in senticnet4.senticnet:
                    emotion = sn.moodtags(word)
                    for emo in emotion:
                        keywords_emotions.append(emo.replace("#",""))

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
        if np.linalg.norm(orderedEmoList) != 0.0:
            normEmoList = orderedEmoList / np.linalg.norm(orderedEmoList)
        
        #append keywords normalized L2 values
        output.append(normEmoList.tolist())
    with open('./movie_raw.txt', 'w') as outfile:
        json.dump(output, outfile)
    with open('./movie_indices.txt', 'w') as outfile:
        json.dump(indices, outfile)
        
if __name__=="__main__":
    processMovieData(build.builddictionary())