from sklearn.cluster import KMeans
from pandas import read_csv
import numpy as np
import json

lyrics = [0.58970719550332,0.016380882276275,0.863911783129826,0.535381599410218,0.556402999059265,0.28556406100863,0.912163440923888,0.418320719872901]

def trainmodel(csv):
    #Fit the model on the data
    kmeans = KMeans(n_clusters=50, random_state=0).fit(csv)
    #Assign each movie to a cluster
    indices = kmeans.predict(csv)
    #Transpose by assigning each cluster its asscociated movies
    res = [[] for i in range(50)]
    for index,cluster in enumerate(indices):
        res[cluster].append(index)
    return kmeans, res

def predict(model,lyrics):
    #Give a new lyrics, predict the cluster it belongs to 
    center = model.predict(lyrics)
    return center

def main():
    #Read txt File containing the movie dataset
    with open('./movie_raw.txt') as json_data:
        txt = json.load(json_data)
    movie_indices = []
    for item in txt:

    #Train and predict the lyrics
    model, clusters = trainmodel(txt)
    predicted_label = predict(model,lyrics = np.array(lyrics).reshape(1,-1))
    #Find the indices of the movies in that cluster
    cluster_movies = clusters[predicted_label[0]]
    #Computer L2 Norm and find the 5 smallest norm values
    scores = []
    for movie in cluster_movies:
        scores.append(np.linalg.norm(txt.values[movie] - lyrics))
    print(np.array(scores).argsort()[::1][:5])


if __name__ == "__main__":
    main()