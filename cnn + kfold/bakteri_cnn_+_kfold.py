# -*- coding: utf-8 -*-
"""Bakteri CNN + KFold.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1flZiD3XerXNCSHtTUJfSXcdTVlPwC2sS
"""

import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, f1_score, precision_score
from sklearn.model_selection import StratifiedKFold
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import random
import os
import shutil
import datetime

datasetFolderName='/content/drive/MyDrive/Colab Notebooks/Bakteri/Dataset'
sourceFiles=[]
classLabels=['Clostridium_perfringens', 'Escherichia_coli', 'Lactobacillus_reuteri', 'Proteus', 'Staphylococcus_epidermidis', 'Streptococcus_agalactiae']

def transferBetweenFolders(source, dest, splitRate):   
    global sourceFiles
    sourceFiles=os.listdir(source)

    if(len(sourceFiles)!=0):
        transferFileNumbers=int(len(sourceFiles)*splitRate)
        transferIndex=random.sample(range(0, len(sourceFiles)), transferFileNumbers)

        for eachIndex in transferIndex:
            shutil.move(source+str(sourceFiles[eachIndex]), dest+str(sourceFiles[eachIndex]))
    else:
        print("No file moved. Source empty!")
        
def transferAllClassBetweenFolders(source, dest, splitRate):
    for label in classLabels:
        transferBetweenFolders(datasetFolderName+'/'+source+'/'+label+'/', 
                               datasetFolderName+'/'+dest+'/'+label+'/', 
                               splitRate)

transferAllClassBetweenFolders('test', 'train', 1.0)
transferAllClassBetweenFolders('train', 'test', 0.20)

X=[]
Y=[]
 
def prepareNameWithLabels(folderName):
    sourceFiles=os.listdir(datasetFolderName+'/train/'+folderName)
    for val in sourceFiles:
        X.append(val)
        if(folderName==classLabels[0]):
            Y.append(0)
        elif(folderName==classLabels[1]):
            Y.append(1)
        elif(folderName==classLabels[2]):
            Y.append(2)
        elif(folderName==classLabels[3]):
            Y.append(3)
        elif(folderName==classLabels[4]):
            Y.append(4)
        else:
            Y.append(5)
 
# Atur nama file dan label kelas dalam variabel X dan Y.
prepareNameWithLabels(classLabels[0])
prepareNameWithLabels(classLabels[1])
prepareNameWithLabels(classLabels[2])
prepareNameWithLabels(classLabels[3])       
prepareNameWithLabels(classLabels[4])       
prepareNameWithLabels(classLabels[5])       
 
X=np.asarray(X)
Y=np.asarray(Y)
 
print(X)
print(Y)

print(len(X))

train_path = datasetFolderName+'/train/'
validation_path = datasetFolderName+'/validation/'
test_path = datasetFolderName+'/test/'
 
num_class = len(classLabels)
print(num_class)

model = Sequential()
 
model.add(Conv2D(16, (3, 3), activation='relu', input_shape=(224, 224, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
 
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_class, activation='softmax'))

tf.keras.utils.plot_model(
    model,
    to_file="model.png",
    show_shapes=True,
    show_dtype=True,
    show_layer_names=True,
    rankdir="TB",
    expand_nested=True,
    dpi=96,
)

model.compile(
    loss="categorical_crossentropy",
    optimizer="adam",
    metrics=['accuracy']
)

datagen = ImageDataGenerator(
        rescale = 1./255,
        shear_range = 0.2
)

skf = StratifiedKFold(n_splits = 3, shuffle = True)
skf.get_n_splits(X, Y)
foldNum = 0
epoch = 50
 
for train_index, val_index in skf.split(X, Y):
    transferAllClassBetweenFolders('validation', 'train', 1.0)
    foldNum+=1
    print("Hasil untuk Fold ke ",foldNum)
    X_train, X_val = X[train_index], X[val_index]
    Y_train, Y_val = Y[train_index], Y[val_index]

    for eachIndex in range(len(X_val)):
        classLabel=''
        if(Y_val[eachIndex]==0):
            classLabel=classLabels[0]
        elif(Y_val[eachIndex]==1):
            classLabel=classLabels[1]
        elif(Y_val[eachIndex]==2):
            classLabel=classLabels[2]
        elif(Y_val[eachIndex]==3):
            classLabel=classLabels[3]
        elif(Y_val[eachIndex]==4):
            classLabel=classLabels[4]
        else:
            classLabel=classLabels[5]   

        shutil.move(datasetFolderName+'/train/'+classLabel+'/'+X_val[eachIndex], 
                    datasetFolderName+'/validation/'+classLabel+'/'+X_val[eachIndex])
        
    train_generator = datagen.flow_from_directory(
        directory = train_path,
        target_size = (224, 224),
        batch_size = 3,
        class_mode = 'categorical',
    )
 
    val_generator = datagen.flow_from_directory(
            directory = validation_path,
            target_size = (224, 224),
            batch_size = 3,
            class_mode = 'categorical',
    )   

    weights = compute_class_weight('balanced', np.unique(train_generator.classes), train_generator.classes)
    cw = dict(zip(np.unique(train_generator.classes), weights))

    early = EarlyStopping(monitor="val_loss", mode="min", patience=3)
    learning_rate_reduction = ReduceLROnPlateau(monitor='val_loss', patience = 3, verbose=1, factor=0.3, min_lr=0.000001)
    callbacks_list = [early, learning_rate_reduction]
   
    # fit model
    history = model.fit(
        train_generator,
        steps_per_epoch = len(train_generator),
        validation_data = val_generator,
        validation_steps = len(val_generator),
        epochs = epoch,
        class_weight = cw,
        callbacks = callbacks_list,
        # verbose = 1
    )

# Save Model
base_path = "/content/drive/My Drive/Colab Notebooks/model"
project_name = "bakteri"
model_name = "bakteri_modelKFold3_224px.h5"
model_path = os.path.join(base_path, project_name, model_name)
model.save(model_path, include_optimizer = False)

# =============TESTING============
from sklearn.metrics import classification_report
# from tensorflow.keras.models import load_model

# MODEL_PATH = '/content/drive/MyDrive/Colab Notebooks/model/bakteri/bakteri_modelKFold3_224px.h5'
# model = load_model(MODEL_PATH, compile = True)

test = '/content/drive/MyDrive/Colab Notebooks/Bakteri/Dataset/test'

test_generator = datagen.flow_from_directory(
        directory = test,
        target_size=(224, 224),
        batch_size = 1,
        class_mode = 'categorical',
        shuffle = False
) 

predictions = model.predict(test_generator, verbose=1)
yPredictions = np.argmax(predictions, axis=1)
true_classes = test_generator.classes

print("\nHasil Sebenarnya Data Test\n{}".format(true_classes))
print("\nHasil Prediksi Data Test\n{}\n".format(yPredictions))
print(classification_report(true_classes, yPredictions, target_names=classLabels))

# ============================================================================================================