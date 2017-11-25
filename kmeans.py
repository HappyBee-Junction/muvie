from sklearn.cluster import KMeans
from pandas import read_csv
import numpy as np
import json

lyrics = [0.58970719550332,0.016380882276275,0.863911783129826,0.535381599410218,0.556402999059265,0.28556406100863,0.912163440923888,0.418320719872901]

def trainmodel(data, movie_indices):
    #Fit the model on the data
    kmeans = KMeans(n_clusters=50, random_state=0).fit(data)
    #Assign each movie to a cluster
    indices = kmeans.predict(data)
    #Transpose by assigning each cluster its asscociated movies
    res = [[] for i in range(50)]
    for index,cluster in enumerate(indices):
        res[cluster].append(movie_indices[index])
    return kmeans, res

def predict(model,lyrics):
    #Give a new lyrics, predict the cluster it belongs to 
    center = model.predict(lyrics)
    return center

def main():
    #Read txt File containing the movie dataset
    with open('./movie_raw.txt') as json_data:
        txt = json.load(json_data)
    with open('./movie_indices.txt') as json_data:
        movie_indices = json.load(json_data)
    #Train and predict the lyrics
    model, clusters = trainmodel(txt, movie_indices)
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