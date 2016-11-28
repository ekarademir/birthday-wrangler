# import pandas as pd
import numpy as np
import codecs, math, pickle, random
from sklearn import model_selection, neural_network, svm, naive_bayes

def nationality_trainer_v1():
    # Load nationality list
    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = list(map(lambda x: x.strip().lower(), f.readlines()))
    # Load words list
    with codecs.open("words.txt", "r", "utf-8") as f:
        words = list(map(lambda x: x.strip().lower(), f.readlines()))

    random.shuffle(words)
    wordstrain = words[0:1*len(nationalities)]
    # Results of nationalities list are true the others are false
    # These will be used in training
    ynat = [1 for x in nationalities]
    ywor = [0 for x in wordstrain]

    y = ynat+ywor

    # Combine all words into a big list and calculate length of each word
    totallist = nationalities + wordstrain
    X = [len(x) for x in totallist]

    # Prepare a matrix whose number of rows is the same as the big list
    # and whose number of cols is the same as the word with max length
    # separate them into letters, then two letters, then three letters
    longest = 25 + 24 + 23# max(X)
    X = np.zeros((len(X), longest), dtype=np.int64)
    # convert each character of each word in the list and save them in the
    # value matrix we created above. For words of length less than max length,
    # remaning col values are zero. Do this for two and three letter pairs
    for i in range(len(totallist)): #
        X[i, 0:len(totallist[i])] = np.array( [ord(x) for x in totallist[i]] )
        #two letters
        for j in range(0,len(totallist[i])-1):
            letter1 = ord(totallist[i][j])
            letter2 = ord(totallist[i][j+1])
            X[i, (25+j)] = int("{0}{1}".format(letter1,letter2))
        #three letters
        for j in range(0,len(totallist[i])-2):
            letter1 = ord(totallist[i][j])
            letter2 = ord(totallist[i][j+1])
            letter3 = ord(totallist[i][j+2])
            X[i, (25+24+j)] = int("{0}{1}{2}".format(letter1,letter2,letter3))

    # Load neural network classifier
    # hiddenlayers = (100,)
    # clf = neural_network.MLPClassifier(hidden_layer_sizes = hiddenlayers)

    # Load Support Vector Machine
    # clf = svm.SVC()

    # Load Naive Bayes
    clf = naive_bayes.MultinomialNB()

    # Use shuffle split for N way splitting
    cv = model_selection.ShuffleSplit(n_splits = 5, test_size = 0.3)
    # score the classifier
    print(model_selection.cross_val_score(clf, X, y,cv=cv))

    # Train the machine and save it
    # clf.fit(X,y)
    # with open("NationalityDetectorNeuralNetwork.pickle", mode='wb') as f:
    #     pickle.dump(clf, f)

def nationality_trainer():
    # Load nationality list
    with codecs.open("nationalities.txt", "r", "utf-8") as f:
        nationalities = list(map(lambda x: x.strip().lower(), f.readlines()))
        nationalities = list(filter(lambda x: len(x) > 3 , nationalities))
    # Load words list
    with codecs.open("words.txt", "r", "utf-8") as f:
        words = list(map(lambda x: x.strip().lower(), f.readlines()))
        words = list(filter(lambda x: len(x) > 3 , words))

    random.shuffle(words)
    wordstrain = words#[0:4*len(nationalities)]
    # Results of nationalities list are true the others are false
    # These will be used in training
    ynat = [1 for x in nationalities]
    ywor = [0 for x in wordstrain]

    y = ynat+ywor

    # Combine all words into a big list and calculate length of each word
    totallist = nationalities + wordstrain
    X = [len(x) for x in totallist]
    print(np.shape(X))

    # Take last three letters of each word
    X = np.zeros( ( len(X), 3 ), dtype = np.int16 )
    # Convert three letters to numbers
    for i in range(len(totallist)): #
        X[i, 0:3] = np.array( [ord(x) for x in totallist[i][-3:]] )

    print(X[-1])
    # Load neural network classifier
    # hiddenlayers = (5,30,45,60,30,15,)
    # clf = neural_network.MLPClassifier(hidden_layer_sizes = hiddenlayers)

    # Load Support Vector Machine
    clf = svm.SVC(kernel='rbf', gamma=1./3.,shrinking=True, tol=1e-3, verbose=True, random_state=42)
    # clf = svm.LinearSVC()

    # Load Naive Bayes
    # clf = naive_bayes.MultinomialNB(alpha=0.5)

    # Use shuffle split for N way splitting
    # cv = model_selection.ShuffleSplit(n_splits = 5, test_size = 0.3, random_state=42)
    # score the classifier
    # print(model_selection.cross_val_score(clf, X, y,cv=cv))

    # Train the machine and save it
    clf.fit(X,y)
    with open("NationalityDetectorSVM.pickle", mode='wb') as f:
        pickle.dump(clf, f)

def is_nationality(test):
    with open("NationalityDetectorSVM.pickle", mode='rb') as f:
        clf = pickle.load(f)

    X = np.zeros( ( 1, 3 ), dtype = np.int16 )
    X[0, 0:3] = np.array( [ord(x) for x in test[-3:]] )

    return bool(clf.predict(X))

if __name__ == '__main__':
    # nationality_trainer()
    print(is_nationality('skiddcan'))
