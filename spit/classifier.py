""" New SPIT Classifier object
"""
from __future__ import (print_function, absolute_import, division, unicode_literals)

import os
import numpy as np
from spit import preprocess
from spit import labels
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import optimizers
import math

class Classifier(object):


  # For Kast, label_dict = labels.kast_label_dict()
  # preproc_dict = preprocess.original_preproc_dict()
  # classify_dict = labels.kast_classify_dict(label_dict)
  def __init__(self, label_dict, preproc_dict, classify_dict, **kwargs):
    self.label_dict = label_dict.copy()
    self.preproc_dict = preproc_dict.copy()
    # is this for prediction? <----
    self.classify_dict = classify_dict.copy() 
    
    # Set up tensorflow/keras model
    self.init_session()
    
  
  # One major change from tf1.0 to tf2.0
  # is that tf.layers module no longer relies on tf.variable_scope
  # and no more use of tf.placeholder
  # no more session.run() although not actual functioning originally 
  def init_session(self):
    
    # building a simple model
    # linear stack of layers

    self.model = keras.Sequential([
        # 2D convolution followed by a maxpool, change data format when actual dataset etc. comes or when testing
        keras.layers.Conv2D(36, kernel_size=5, strides=(1, 1), padding='valid', activation='relu', 
                            input_shape = (self.preproc_dict['image_height'], self.preproc_dict['image_width'], self.preproc_dict['num_channels'])),
        keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2, padding='valid'),
        # And another, this time with 64 filters instead of 36
        keras.layers.Conv2D(64, kernel_size=5, strides=(1, 1), activation='relu'),
        keras.layers.MaxPooling2D(pool_size=(2, 2), strides=2, padding='valid'),
        # Flatten in preparation for FC layer
        keras.layers.Flatten(),
        # FC layer
        keras.layers.Dense(units=128, activation='relu'),
        # Produce 0-1 probabilities with softmax
        keras.layers.Dense(len(self.label_dict), activation='softmax')
    ])
    # convert labels to respective categories for training
    self.y_train = keras.utils.to_categorical(list(self.label_dict.values()), 
                                              num_classes=len(self.label_dict))
    # add optimizer, learning rate, and loss function
    adam = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

    self.model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])#, rate=1e-4)
    return

  def load_model(self, file_name, file_path):
    '''

    :param file_name: The model name. Should be a string 'blah.h5'
           file_path: The path that the user would like to save to.
                      In the form of 'blah/foo/bar/'
    :return: the model loaded
    '''

    loaded_model = keras.models.load_model(file_path+file_name)
    return loaded_model

  def save_model(self, model_to_save, file_name, file_path):
    '''

    :param file_name: The model name. Should be a string 'blah.h5'
           file_path: The path that the user would like to save to.
                      In the form of 'blah/foo/bar/'
    :return: N/A
    '''

    model_to_save.save(file_path+file_name)
    return
  
  def evaluate(self, test_images, test_labels, test_model=None):
    """
    Evaluate the model on an unseen dataset.
    Assume the model is constructed and trained already.

    :param test_model:
        An alternative choice for model to test.
    :param test_images:
        Set of test images not seen by the model yet.
        Assume this is a numpy array with (batch_size, width, height, num_channels) as its dimensions.
    :param test_labels:
        Set of test labels corresponding to test images.
        Assume this is a vector with (batch_size, 1) as its dimensions.

    :return:
      loss: Loss of the evaluated model as a float value.
      acc: Accuracy of the evaluated model as a float value between 0 and 1.
    """

    # make categorical for model
    y_test = keras.utils.to_categorical(test_labels, num_classes=len(self.label_dict))
    # evaluate model
    if test_model is None:
      loss, acc = self.model.evaluate(test_images, y_test)
    else:
      loss, acc = test_model.evaluate(test_images, y_test)
    # return loss and accuracy as array
    return loss, acc
  
  def compare_with_best(self, test_dset, test_labels, file_path):
    '''
    Method to compare current model with the best_model and save a new best_model
    :param test_dset: test data
    :param test_labels: test labels
    :param file_path: where to save the model. In the form 'blah/foo/bar/'
    :return: N/A
    '''

    try:
      best_model = self.load_model('best_model.h5', file_path)
      has_best = True
    except:
      has_best = False
      pass

    if has_best:
      loss_self, acc_self = self.evaluate(test_dset, test_labels)
      loss_best, acc_best = self.evaluate(test_dset, test_labels, test_model=best_model)
      if acc_self > acc_best:
        self.save_model(self.model, 'best_model.h5', file_path)
        del best_model
      else:
        del best_model
    else:
      self.save_model(self.model, 'best_model.h5', file_path)

    return

    # Other architectures
    """
    with pt.defaults_scope(activation_fn=tf.nn.relu):
        y_pred, loss = x_pretty.\
            conv2d(kernel=5, depth=16, name='layer_conv1').\
            max_pool(kernel=2, stride=2).\
            conv2d(kernel=5, depth=36, name='layer_conv2').\
            max_pool(kernel=2, stride=2).\
            flatten().\
            fully_connected(size=128, name='layer_fc1').\
            softmax_classifier(num_classes=num_classes, labels=y_true)
    """

    """
    with pt.defaults_scope(activation_fn=tf.nn.relu):
        y_pred, loss = x_pretty.\
            conv2d(kernel=5, depth=36, name='layer_conv1').\
            conv2d(kernel=5, depth=64, name='layer_conv2').\
            conv2d(kernel=5, depth=72, name='layer_conv2').\
            conv2d(kernel=5, depth=102, name='layer_conv2').\
            max_pool(kernel=2, stride=2).\
            flatten().\
            fully_connected(size=256, name='layer_fc1').\
            fully_connected(size=128, name='layer_fc1').\
            softmax_classifier(num_classes=num_classes, labels=y_true)
    """

    """
    with pt.defaults_scope(activation_fn=tf.nn.relu):
        y_pred, loss = x_pretty.\
            conv2d(kernel=5, depth=64, name='layer_conv1').\
            max_pool(kernel=2, stride=2).\
            conv2d(kernel=5, depth=64, name='layer_conv2').\
            max_pool(kernel=2, stride=2).\
            flatten().\
            fully_connected(size=256, name='layer_fc1').\
            fully_connected(size=128, name='layer_fc2').\
            softmax_classifier(num_classes=num_classes, labels=y_true)
    """
