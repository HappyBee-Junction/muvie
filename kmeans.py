from sklearn.cluster import KMeans
from pandas import read_csv
from scipy import stats
import numpy as np
import json, requests, collections
import build, senticnet4
import math as m
# import matplotlib.pyplot as plt
# from sklearn.decomposition import PCA

alphDict = {'admiration': 0, 'anger': 0, 'disgust': 0, 'fear': 0, 'interest': 0 , 'joy': 0, 'sadness': 0, 'surprise': 0}

##---------Train Model------------##
#Read txt File containing the dataset
with open('./movie_raw.txt') as json_data:
    txt = json.load(json_data)
with open('./movie_indices.txt') as json_data:
    movie_indices = json.load(json_data)
with open('./stopwords.txt') as json_data:
    STOPWORDS = json.load(json_data)

num_cluster = 100
#Fit the model on the data
model = KMeans(n_clusters=num_cluster, random_state=0).fit(txt)
#Assign each movie to a cluster
indices = model.predict(txt)  # ----pythonic indices
#Transpose by assigning each cluster its asscociated movies
clusters = [[] for i in range(num_cluster)]
for index, cluster in enumerate(indices):
    clusters[cluster].append(index)
dic = build.builddictionary()
##---------End Train Model------------##

##---------Visualization Code------------##
# reduced_data = PCA(n_components=2).fit_transform(txt)
# kmeans = KMeans(init='k-means++', n_clusters=num_cluster)
# kmeans.fit(reduced_data)

# # Step size of the mesh. Decrease to increase the quality of the VQ.
# h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

# # Plot the decision boundary. For that, we will assign a color to each
# x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
# y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
# xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

# # Obtain labels for each point in mesh. Use last trained model.
# Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])

# # Put the result into a color plot
# Z = Z.reshape(xx.shape)
# plt.figure(1)
# plt.clf()
# plt.imshow(Z, interpolation='nearest',
#            extent=(xx.min(), xx.max(), yy.min(), yy.max()),
#            cmap=plt.cm.Paired,
#            aspect='auto', origin='lower')

# plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
# # Plot the centroids as a white X
# centroids = kmeans.cluster_centers_
# plt.scatter(centroids[:, 0], centroids[:, 1],
#             marker='x', s=169, linewidths=3,
#             color='w', zorder=10)
# plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
#           'Centroids are marked with white cross')
# plt.xlim(x_min, x_max)
# plt.ylim(y_min, y_max)
# plt.xticks(())
# plt.yticks(())
# plt.show()
##---------End Visualization Code------------##

def findemotion(word):
    sn = senticnet4.senticnet
    emotions = []
    for s in sn[word]:
        if '#' in s:
            emotions.append(s)
    return emotions

def processLyrics(data):
    final_emotions = [0.0] * 8
    for item in data:
        if item[0] == '':
            continue
        lyrics_string = item[0]
        features = item[1]
        lyrics = lyrics_string.split(' ')
        emotions = []
        for word in lyrics:
            if word not in STOPWORDS and word in senticnet4.senticnet:
                emotion = findemotion(word)
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
        dance_direct = features['danceability'] * 2
        dance_inv = (1.0 - features['danceability']) * 2
        
        energy_direct = features['energy'] * 2
        energy_inv = (1.0 - features['energy']) * 2

        tempo_direct = features['tempo']/100.0
        tempo_inv = 100.0/features['tempo']
        
        loudness_direct = (features['loudness'] + 60.0) / 35.0
        loudness_inv = m.fabs(10 - features['loudness']) / 35.0        

        orderedEmoLycList[1] = orderedEmoLycList[1] * dance_inv
        orderedEmoLycList[1] = orderedEmoLycList[1] * energy_direct
        orderedEmoLycList[1] = orderedEmoLycList[1] * loudness_direct

        orderedEmoLycList[5] = orderedEmoLycList[5] * dance_direct
        orderedEmoLycList[5] = orderedEmoLycList[5] * tempo_direct
        
        orderedEmoLycList[6] = orderedEmoLycList[6] * dance_inv
        orderedEmoLycList[6] = orderedEmoLycList[6] * energy_inv
        orderedEmoLycList[6] = orderedEmoLycList[6] * tempo_inv
        orderedEmoLycList[6] = orderedEmoLycList[6] * loudness_inv                
        
        final_emotions = np.array(final_emotions) + np.array(orderedEmoLycList)

    final_emotions[0] = final_emotions[0] * 0.7
    final_emotions[2] = final_emotions[2] * 0.7
    final_emotions[4] = final_emotions[4] * 0.7
    final_emotions[7] = final_emotions[7] * 0.7

    if np.linalg.norm(final_emotions) != 0.0:
        final_emotions = final_emotions / np.linalg.norm(final_emotions)
    #normalized(sortedList[::-1][:5]) #append keywords
    return final_emotions

def predict(lyrics):
    #Give a new lyrics, predict the cluster it belongs to
    center = model.predict(lyrics)
    return center

##-------Call this function to classify songs-----##
def kmeans(lyrics):
    # with open('./songs_data.txt', 'w') as outfile:
    #     json.dump(lyrics, outfile)
    # with open('./songs_data.txt') as json_data:
    #     txt = json.load(json_data)
    lyrics_emotions = processLyrics(lyrics)
    # lyrics_emotions = processLyrics(txt)
    
    lyrics = np.array(lyrics_emotions).reshape(1, -1)
    predicted_label = predict(lyrics)
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
    values = ['admiration', 'anger', 'disgust', 'fear', 'interest' , 'joy', 'sadness', 'surprise']
    dic = [[] for i in range(8)]
    for index,emotions in enumerate(lyrics_emotions):
        dic[index].append(values[index])
        dic[index].append(emotions)
    return movie_ids, dict(dic)

def main():
    s = "I'm living on an endless road Around the world for rock and roll Sometimes it feels so tough But I still ain't had enough I keep saying that it's getting too much But I know I'm a liar Feeling all right in the noise and the light But that's what lights my fire Hellraiser, in the thunder and heat Hellraiser, rock you back in your seat Hellraiser, and I'll make it come true Hellraiser, I'll put a spell on you Walking out on another stage Another town, another place Sometimes I don't feel right Nerves wound up too damn tight Don't you tell me it's bad for my health But kicking back don't make it Out of control, I play the ultimate role Don't know how to make it Hellraiser, in the thunder and heat Hellraiser, rock you back in your seat Hellraiser, and I'll make it come true Hellraiser, I'll put a spell on you I'm living on an endless road Around the world for rock and roll Sometimes it feels so tough But I still ain't had enough I keep saying that it's getting too much But I know I'm a liar Feeling all right in the noise and the light But that's what lights my fire Hellraiser, in the thunder and heat Hellraiser, rock you back in your seat Hellraiser, and I'll make it come true Hellraiser, I'll put a spell on you"
    print(kmeans(s))

if __name__ == "__main__":
    main()