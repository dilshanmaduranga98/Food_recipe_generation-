# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EBN39paM64jmI2kyQJt6zWqbFS55Khrl
"""

import numpy as np
import pandas as pd
from pathlib import Path
import os.path
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img,img_to_array

from google.colab import drive
drive.mount('/content/drive')

train_dir = Path('/content/drive/My Drive/Final Project/Fast food Dataset/Train')
train_filepath = list(train_dir.glob(r'**/*.jpeg'))

test_dir = Path('/content/drive/My Drive/Final Project/Fast food Dataset/Test')
test_filepath = list(test_dir.glob(r'**/*.jpeg'))

valid_dir = Path('/content/drive/My Drive/Final Project/Fast food Dataset/Valid')
valid_filepath = list(valid_dir.glob(r'**/*.jpeg'))

def image_processing(filepath):

  labels = [str(filepath[i]).split("/")[7]\
            for i in range(len(filepath))]

  filepath = pd.Series(filepath, name='Filepath').astype(str)
  labels = pd.Series(labels, name='Label')

  #concataneta filepath and labels
  df = pd.concat([filepath, labels], axis=1)

  #shuffle the dataframe and rest indexes
  df = df.sample(frac=1).reset_index(drop = True)

  return df

train_df = image_processing(train_filepath)
test_df = image_processing(test_filepath)
valid_df = image_processing(valid_filepath)

print('--- Traing set --- \n')
print(f'1. No of images : {train_df.shape[0]}\n')
print(f'2. No of Different labels: {len(train_df.Label.unique())}\n')
print(f'3. Labels: {train_df.Label.unique()}')

print('************************************************** \n')
print('************************************************** \n')

print('--- Test set --- \n')
print(f'1. No of images : {test_df.shape[0]}\n')
print(f'2. No of Different labels: {len(test_df.Label.unique())}\n')
print(f'3. Labels: {test_df.Label.unique()}')

print('************************************************** \n')
print('************************************************** \n')

print('--- Validation set --- \n')
print(f'1. No of images : {valid_df.shape[0]}\n')
print(f'2. No of Different labels: {len(valid_df.Label.unique())}\n')
print(f'3. Labels: {valid_df.Label.unique()}')

valid_df.head(10)

#create dataframe with one labale with each category
df_unique = train_df.copy().drop_duplicates(subset=["Label"]).reset_index()

#display picture of the dataset(some)
fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(10, 8), subplot_kw={'xticks':[], 'yticks':[]})

for i, ax in enumerate(axes.flat):
    ax.imshow(plt.imread(df_unique.Filepath[i]))
    ax.set_title(df_unique.Label[i], fontsize = 10)
plt.tight_layout(pad=0.5)
plt.show()

train_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function = tf.keras.applications.mobilenet_v2.preprocess_input
)

test_generator = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function = tf.keras.applications.mobilenet_v2.preprocess_input
)

train_images = train_generator.flow_from_dataframe(
    dataframe=train_df,
    x_col='Filepath',
    y_col='Label',
    traget_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=True,
    seed=0,
    rotation_range=30,
    Zoom_range=0.15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest"
)

valid_images = train_generator.flow_from_dataframe(
    dataframe=valid_df,
    x_col='Filepath',
    y_col='Label',
    traget_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=True,
    seed=0,
    rotation_range=30,
    Zoom_range=0.15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest"
)

test_images = test_generator.flow_from_dataframe(
    dataframe=test_df,
    x_col='Filepath',
    y_col='Label',
    traget_size=(224,224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=True,
    seed=0,
    rotation_range=30,
    Zoom_range=0.15,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    horizontal_flip=True,
    fill_mode="nearest"
)

pretrained_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)

pretrained_model.trainable = False

inputs = pretrained_model.input
x = tf.keras.layers.Dense(128, activation='relu')(pretrained_model.output)
x = tf.keras.layers.Dense(128, activation='relu')(x)

outputs = tf.keras.layers.Dense(6, activation='softmax')(x)

model = tf.keras.Model(inputs=inputs, outputs=outputs)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

history = model.fit(
    train_images,
    validation_data=valid_images,
    batch_size = 32,
    epochs=5,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=4,
            restore_best_weights=True
        )
    ]
)

history_df = pd.DataFrame(history.history)
print(history_df[['accuracy', 'val_accuracy', 'loss', 'val_loss']] )


plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='training accuracy')
plt.plot(history.history['val_accuracy'], label='validation accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()


plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='training loss')
plt.plot(history.history['val_loss'], label='validation loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()

#predict the label of test image
pred = model.predict(test_images)
pred = np.argmax(pred,axis=1)

#map the model
labels = (train_images.class_indices)
labels = dict((v,k) for k,v in labels.items())
pred1 = [labels[k] for k in pred]
pred1

def output(location):
    img = load_img(location, target_size = (224,224,3))
    img = img_to_array(img)
    img = img/255
    img = np.expand_dims(img,[0])
    answer = model.predict(img)
    y_class = answer.argmax(axis=-1)
    y = " ".join(str(x) for x in y_class)
    y = int(y)
    res = labels[y]
    return res

img  = output('/content/Pizza.jpg')
img

model.save('FV.h5')

