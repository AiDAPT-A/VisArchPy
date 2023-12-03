"""
Loads pretrained models for its use in the VisArchPy package.
"""

import pickle


class KmeansBbox20:
    """
    Kmeans model for Bbox plot with 20 clusters.
    """

    def __init__(self):

        with open('./src/visarchpy/models/kmeans_bbox20.pkl', 'rb') as f:
            predictor = pickle.load(f)

        self.predictor = predictor

    def __call__(self):
        return self.predictor
