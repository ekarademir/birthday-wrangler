# import pandas as pd
import numpy as np
import codecs, math, pickle
from sklearn import model_selection, neural_network, svm

def nationality_trainer():
    # Load nationality list
    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = list(map(lambda x: x.strip().lower(), f.readlines()))
    # Load words list
    with codecs.open("words.txt", "r", "utf-8") as f:
        words = list(map(lambda x: x.strip().lower(), f.readlines()))

    words = words[0:len(nationalities)]
    # Results of nationalities list are true the others are false
    # These will be used in training
    ynat = [1 for x in nationalities]
    ywor = [0 for x in words]

    y = ynat+ywor

    # Combine all words into a big list and calculate length of each word
    totallist = nationalities + words
    X = [len(x) for x in totallist]

    # Prepare a matrix whose number of rows is the same as the big list
    # and whose number of cols is the same as the word with max length
    longest = 25# max(X)
    X = np.zeros((len(X), longest))
    # convert each character of each word in the list and save them in the
    # value matrix we created above. For words of length less than max length,
    # remaning col values are zero
    for i in range(len(totallist)):
        X[i, 0:len(totallist[i])] = np.array( [ord(x) for x in totallist[i]] )

    # Load neural network classifier
    hiddenlayers = (longest,25,50,75,50,10,5,)
    clf = neural_network.MLPClassifier(hidden_layer_sizes = hiddenlayers)

    # Load Support Vector Machine
    # clf = svm.SVC()

    # Use shuffle split for N way splitting
    cv = model_selection.ShuffleSplit(n_splits = 5, test_size = 0.3)
    # score the classifier
    print(model_selection.cross_val_score(clf, X, y,cv=cv))

    # Train the machine and save it
    clf.fit(X,y)
    with open("NationalityDetectorNeuralNetwork.pickle", mode='wb') as f:
        pickle.dump(clf, f)

def main():
    with open("NationalityDetectorNeuralNetwork.pickle", mode='rb') as f:
        clf = pickle.load(f)

    longest = 25
    test = "german"
    X = np.zeros((1, longest))
    X[0, 0:len(test)] = np.array( [ord(x) for x in test] )

    print(X)
    print(clf.predict(X))

if __name__ == '__main__':
    # nationality_trainer()
    main()
