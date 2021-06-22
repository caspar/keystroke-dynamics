import pickle, os
import numpy as np
from keyboard import collect
from preprocess.preprocessed import transform
from tensorflow.keras.models import load_model
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def preprocess(data, user, pwd_length):

    def loadParameters():
        with open('./authio/model/save/parameters.pkl', 'rb') as f:  
            mu, std = pickle.load(f)
        return mu, std

    line = [e for ele in data[0] for e in ele]

    userID = 0 if user == "yuming" else 1
    
    input_data = transform(userID, 0, 1, line, pwd_length, demo_mode=True)

    mu, std = loadParameters()

    input_data = (input_data[3:] - mu) / std

    return np.array([input_data])

def loadModel(user):

    userID = 0 if user == "yuming" else 1

    model = load_model(f"./authio/model/save/model{userID}", compile=False)

    return model

def verification(model, input_data, user):

    prediction = model.predict(input_data)

    if prediction[0][1] > prediction[0][0]:
        print(f"You are {user}! Let's login!")
    else:
        print(f"You bad guy. How dare you trying to hack into {user}'s account!")

def main():

    data, user, pwd_length = collect(1, 0, demo_mode=True)

    input_data = preprocess(data, user, pwd_length) 

    model = loadModel(user)

    verification(model, input_data, user)

if __name__ == '__main__':
    main()
