#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import numpy as np
from NumPyNet.exception import LayerError
from NumPyNet.utils import check_is_fitted
from NumPyNet.layers.base import BaseLayer

__author__ = ['Mattia Ceccarelli', 'Nico Curti']
__email__ = ['mattia.ceccarelli3@studio.unibo.it', 'nico.curti2@unibo.it']


class Dropout_layer(BaseLayer):

  def __init__(self, prob, input_shape=None, **kwargs):
    '''
    Dropout Layer: drop a random selection of Inputs. This helps avoid overfitting.

    Parameters
    ----------
      prob : float between 0. and 1., probability for every entry to be set to zero.
      input_shape : tuple of 4 integers: input shape of the layer.
    '''

    if prob >= 0. and prob <= 1.:
      self.probability = prob

    else :
      raise ValueError('DropOut layer : parameter "prob" must be 0. < prob < 1., but it is {}'.format(prob))

    if prob != 1.:
      self.scale = 1. / (1. - prob)
    else:
      self.scale = 1. # it doesn't matter anyway, since everything is zero

    self.rnd  = None
    super(Dropout_layer, self).__init__(input_shape=input_shape)

  def __str__(self):
    batch, out_width, out_height, out_channels = self.out_shape
    return 'dropout       p = {0:.2f} {1:4d} x{2:4d} x{3:4d} x{4:4d}   ->  {1:4d} x{2:4d} x{3:4d} x{4:4d}'.format(
           self.probability,
           batch, out_width , out_height , out_channels)

  def forward(self, inpt):
    '''
    Forward function of the Dropout layer: it create a random mask for every input
      in the batch and set to zero the chosen values. Other pixels are scaled
      with the scale variable.

    Parameters
    ----------
      inpt : numpy array of shape (batch, w, h, c), input of the layer

    Returns
    ----------
      Dropout layer object
    '''
    self._check_dims(shape=self.out_shape, arr=inpt, func='Forward')

    self.rnd = np.random.uniform(low=0., high=1., size=self.out_shape) >= self.probability
    self.output = self.rnd * inpt * self.scale
    self.delta  = np.zeros(shape=inpt.shape)

    return self

  def backward(self, delta=None):
    '''
    Backward function of the Dropout layer: given the same mask as the layer
      it backprogates delta only to those pixel which values has not been set to zero
      in the forward.

    Parameters
    ----------
      delta : numpy array of shape (batch, w, h, c), default value is None.
            If given, is the global delta to be backpropagated

    Returns
    ----------
      Dropout layer object
    '''

    check_is_fitted(self, 'delta')
    self._check_dims(shape=self.out_shape, arr=delta, func='Backward')

    if delta is not None:
      self.delta = self.rnd * delta[:] * self.scale
      delta[:] = self.delta.copy()

    return self


if __name__ == '__main__':

  import os

  import pylab as plt
  from PIL import Image

  np.random.seed(123)

  img_2_float = lambda im : ((im - im.min()) * (1./(im.max() - im.min()) * 1.)).astype(float)
  float_2_img = lambda im : ((im - im.min()) * (1./(im.max() - im.min()) * 255.)).astype(np.uint8)

  filename = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dog.jpg')
  inpt = np.asarray(Image.open(filename), dtype=float)
  inpt.setflags(write=1)
  inpt = img_2_float(inpt)

  inpt = np.expand_dims(inpt, axis=0)

  prob = 0.1

  layer = Dropout_layer(input_shape=inpt.shape, prob=prob)

  # FORWARD

  layer.forward(inpt)
  forward_out = layer.output

  print(layer)

  # BACKWARD

  delta = np.ones(shape=inpt.shape, dtype=float)
  layer.delta = np.ones(shape=layer.out_shape, dtype=float)
  layer.backward(delta)

  # Visualitations

  fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(10, 5))
  fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.15)

  fig.suptitle('Dropout Layer\nDrop Probability : {}'.format(prob))
  # Shown first image of the batch
  ax1.imshow(float_2_img(inpt[0]))
  ax1.set_title('Original image')
  ax1.axis('off')

  ax2.imshow(float_2_img(layer.output[0]))
  ax2.set_title('Forward')
  ax2.axis('off')

  ax3.imshow(float_2_img(delta[0]))
  ax3.set_title('Backward')
  ax3.axis('off')

  fig.tight_layout()
  plt.show()
