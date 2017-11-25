from pandas import read_csv
import json
from senticnet.senticnet import Senticnet
import re
from scipy import stats
import numpy as np
import requests
import build
import senticnet4

array = ['id','genres', 'keywords','overview', 'release_date', 'runtime', 'tagline', 'title', 'vote_average']

def getCount(tuple):
    return int(tuple[1])

def normalized(arr):
    sum = 0.0
    for item in arr:
        sum += int(item[1])
    for item in arr:
        item[1] = int(item[1])/sum
    return arr

def processMovieData(dic):
    with open('./stopwords.txt') as json_data:
        STOPWORDS = json.load(json_data)
    sn = Senticnet()
    output = []
    filedata = read_csv('tmdb_5000_movies.csv',skiprows=[1])
    for line in filedata.values:
        data = []
        data.append(line[2]) #append id
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
                if word not in STOPWORDS and word in dic:
                    emotion = sn.moodtags(word)
                    for emo in emotion:
                        keywords_emotions.append(emo.replace("#",""))
        dic_copy = dic.copy()
        sortedList = sorted(stats.itemfreq(overview_emotions + keywords_emotions), key=getCount)
        data.append(normalized(sortedList[::-1][:5])) #append keywords
        output.append(data)
    with open('./movie_raw.txt', 'w') as outfile:
        json.dump(output, outfile)

lyrics = "There's a lady who's sure All that glitters is gold And she's buying a stairway to heaven When she gets there she knows If the stores are all closed With a word she can get what she came for Oh oh oh oh and she's buying a stairway to heaven There's a sign on the wall But she wants to be sure 'Cause you know sometimes words have two meanings In a tree by the brook There's a songbird who sings Sometimes all of our thoughts are misgiving Ooh, it makes me wonder Ooh, it makes me wonder There's a feeling I get When I look to the west And my spirit is crying for leaving In my thoughts I have seen Rings of smoke through the trees And the voices of those who standing looking Ooh, it makes me wonder Ooh, it really makes me wonder And it's whispered that soon, If we all call the tune Then the piper will lead us to reason And a new day will dawn For those who stand long And the forests will echo with laughter If there's a bustle in your hedgerow Don't be alarmed now It's just a spring clean for the May queen Yes, there are two paths you can go by But in the long run There's still time to change the road you're on And it makes me wonder Your head is humming and it won't go In case you don't know The piper's calling you to join him Dear lady, can you hear the wind blow And did you know Your stairway lies on the whispering wind And as we wind on down the road Our shadows taller than our soul There walks a lady we all know Who shines white light and wants to show How everything still turns to gold And if you listen very hard The tune will come to you at last When all are one and one is all To be a rock and not to roll And she's buying the stairway to heaven"

def processLyrics():
    dic = build.builddictionary()
    model = processMovieData(dic)
    lyrics = requests.get("http://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id=15953433&apikey=a861047a0eb1272708e4d518bee92a6d")
    lyrics_ = re.findall(r"[\w']+", lyrics.replace("'"," ")) 
    with open('./stopwords.txt') as json_data:
        STOPWORDS = json.load(json_data)
    sn = Senticnet()
    emotions = []
    for word in lyrics_:
        if word not in STOPWORDS and word in senticnet4.senticnet:
            emotion = sn.moodtags(word)
            for emo in emotion:
                emotions.append(emo.replace("#",""))
    sortedList = sorted(stats.itemfreq(emotions), key=getCount)
    final_emotions = normalized(sortedList[::-1][:5]) #append keywords
    print(final_emotions)

if __name__=="__main__":
    processLyrics()