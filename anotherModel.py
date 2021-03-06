# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 20:40:34 2018

@author: test
"""

from __future__ import print_function
import numpy as np
import cPickle

np.random.seed(1337) # for reproducibililty

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.utils import np_utils

# split data into train,vavlid and test
# train:320
# valid:40
# test:40
def split_data(fname):
    f = open(fname,'rb')
    face_data,face_label = cPickle.load(f)

    X_train = np.empty((555, img_rows * img_cols))
    Y_train = np.empty(555, dtype=int)

    X_valid = np.empty((111, img_rows* img_cols))
    Y_valid = np.empty(111, dtype=int)

    X_test = np.empty((111, img_rows* img_cols))
    Y_test = np.empty(111, dtype=int)

    for i in range(40):
        X_train[i*8:(i+1)*8,:] = face_data[i*10:i*10+8,:]
        Y_train[i*8:(i+1)*8] = face_label[i*10:i*10+8]

        X_valid[i] = face_data[i*10+8,:]
        Y_valid[i] = face_label[i*10+8]

        X_test[i] = face_data[i*10+9,:]
        Y_test[i] = face_label[i*10+9]
    
    return (X_train, Y_train, X_valid, Y_valid, X_test, Y_test)

if __name__=='__main__':
    batch_size = 10
    nb_classes = 40
    nb_epoch = 12

    # input image dimensions
    img_rows, img_cols = 57, 47
    # number of convolutional filters to use
    nb_filters = 32
    # size of pooling area for max pooling
    nb_pool = 2
    # convolution kernel size
    nb_conv = 3
    path='./img2array1.bin'
    (X_train, Y_train, X_valid, Y_valid, X_test, Y_test) = split_data(path)
    X_train = X_train.reshape(X_train.shape[0], 1, img_rows, img_cols)
    X_test = X_test.reshape(X_test.shape[0], 1, img_rows, img_cols)
    
    print('X_train shape:', X_train.shape)
    print(X_train.shape[0], 'train samples')
    print(X_test.shape[0], 'test samples')
    # convert label to binary class matrix
    Y_train = np_utils.to_categorical(Y_train, nb_classes)
    Y_test = np_utils.to_categorical(Y_test, nb_classes)

    model = Sequential()
    # 32 convolution filters , the size of convolution kernel is 3 * 3
    # border_mode can be 'valid' or 'full'
    #‘valid’only apply filter to complete patches of the image. 
    # 'full'  zero-pads image to multiple of filter shape to generate output of shape: image_shape + filter_shape - 1
    # when used as the first layer, you should specify the shape of inputs 
    # the first number means the channel of an input image, 1 stands for grayscale imgs, 3 for RGB imgs
    model.add(Convolution2D(nb_filters, nb_conv, nb_conv,
                            border_mode='valid',
                            input_shape=(1, img_rows, img_cols)))
    # use rectifier linear units : max(0.0, x)
    model.add(Activation('relu'))
    # second convolution layer with 32 filters of size 3*3
    model.add(Convolution2D(nb_filters, nb_conv, nb_conv))
    model.add(Activation('relu'))
    # max pooling layer, pool size is 2 * 2
    model.add(MaxPooling2D(pool_size=(nb_pool, nb_pool)))
    # drop out of max-pooling layer , drop out rate is 0.25 
    model.add(Dropout(0.25))
    # flatten inputs from 2d to 1d
    model.add(Flatten())
    # add fully connected layer with 128 hidden units
    model.add(Dense(128))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    # output layer with softmax 
    model.add(Dense(nb_classes))
    model.add(Activation('softmax'))
    # use cross-entropy cost and adadelta to optimize params
    model.compile(loss='categorical_crossentropy', optimizer='adadelta')
    # train model with bath_size =10, epoch=12
    # set verbose=1 to show train info
    model.fit(X_train, Y_train, batch_size=batch_size, nb_epoch=nb_epoch,
          show_accuracy=True, verbose=1, validation_data=(X_test, Y_test))
    # evaluate on test set
    score = model.evaluate(X_test, Y_test, show_accuracy=True, verbose=0)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])