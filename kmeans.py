from sklearn.cluster import KMeans
from pandas import read_csv
from scipy import stats
import numpy as np
import json, requests, collections
import build, senticnet4
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

num_cluster = 50
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
# kmeans = KMeans(init='k-means++', n_clusters=5)
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

def processLyrics(lyrics):
    lyrics = lyrics.split(' ')
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
    if np.linalg.norm(orderedEmoLycList) != 0.0:
        final_emotions = orderedEmoLycList / np.linalg.norm(orderedEmoLycList)
    #normalized(sortedList[::-1][:5]) #append keywords
    return final_emotions

def predict(lyrics):
    #Give a new lyrics, predict the cluster it belongs to
    center = model.predict(lyrics)
    return center

##-------Call this function to classify songs-----##
def kmeans(lyrics):
    lyrics_emotions = processLyrics(lyrics)
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
    return movie_ids

def main():
    s = "So long I've been looking too hard I've been waiting too long Sometimes I don't know what I will find I only know it's a matter of time When you love someone When you love someone It feels so right, so warm and true I need to know if you feel it too Maybe I'm wrong Won't you tell me if I'm coming on too strong This heart of mine has been hurt before This time I wanna be sure I've been waiting for a girl like you To come into my life I've been waiting for a girl like you A love that will survive I've been waiting for someone new To make me feel alive Yeah, waiting for a girl like you To come into my life You're so good When we make love It's understood It's more than a touch or a word we say Only in dreams could it be this way When you love someone Yeah, really love someone Now I know it's right From the moment I wake up 'til deep in the night There's nowhere on earth that I'd rather be Than holding you tenderly I've been waiting for a girl like you To come into my life I've been waiting for a girl like you A love that will survive I've been waiting for someone new To make me feel alive Yeah, waiting for a girl like you To come into my life I've been waiting Waiting for you I've been waiting I've been waiting, yeah (I've been waiting for a girl like you I've been waiting) Won't you come into my life?"
    print(kmeans(s))

if __name__ == "__main__":
    main()