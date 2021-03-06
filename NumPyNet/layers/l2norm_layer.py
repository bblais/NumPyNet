#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

import numpy as np
from NumPyNet.utils import check_is_fitted
from NumPyNet.layers.base import BaseLayer

__author__ = ['Mattia Ceccarelli', 'Nico Curti']
__email__ = ['mattia.ceccarelli3@studio.unibo.it', 'nico.curti2@unibo.it']


class L2Norm_layer(BaseLayer):

  def __init__(self, input_shape=None, axis=None, **kwargs):
    '''
    L2Norm layer

    Parameters
    ----------
      input_shape : tuple of 4 integers: input shape of the layer.
      axis : integer, default None. Axis along which the vector is normalized.
        If None, the norm is computed along the whole vector.
    '''

    self.axis = axis
    self.scales = None

    super(L2Norm_layer, self).__init__(input_shape=input_shape)

  def __str__(self):
    batch, w, h, c = self.out_shape
    return 'l2norm                 {0:>4d} x{1:>4d} x{2:>4d} x{3:>4d}   ->  {0:>4d} x{1:>4d} x{2:>4d} x{3:>4d}'.format(
           batch, w, h, c)

  def forward(self, inpt):
    '''
    Forward of the l2norm layer, apply the l2 normalization over
    the input along the given axis

    Parameters
    ----------
      inpt: numpy array, the input to be normalized.

    Returns
    -------
      L2norm_layer object
    '''

    self._check_dims(shape=self.input_shape, arr=inpt, func='Forward')

    norm = (inpt * inpt).sum(axis=self.axis, keepdims=True)
    norm = 1. / np.sqrt(norm + 1e-8)
    self.output = inpt * norm
    self.scales = (1. - self.output) * norm
    self.delta  = np.zeros(shape=self.out_shape, dtype=float)

    return self

  def backward(self, delta):
    '''
    Compute the backward of the l2norm layer

    Parameters
    ----------
      delta : numpy array, global error to be backpropagated.

    Returns
    -------
      L2norm_layer object
    '''

    check_is_fitted(self, 'delta')
    self._check_dims(shape=self.input_shape, arr=delta, func='Backward')

    self.delta += self.scales
    delta[:]   += self.delta

    return self


if __name__ == '__main__':

  import os

  import pylab as plt
  from PIL import Image

  img_2_float = lambda im : ((im - im.min()) * (1./(im.max() - im.min()) * 1.)).astype(float)
  float_2_img = lambda im : ((im - im.min()) * (1./(im.max() - im.min()) * 255.)).astype(np.uint8)

  filename = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'dog.jpg')
  inpt = np.asarray(Image.open(filename), dtype=float)
  inpt.setflags(write=1)
  inpt = img_2_float(inpt)

  # add batch = 1
  inpt = np.expand_dims(inpt, axis=0)

  layer = L2Norm_layer(input_shape=inpt.shape)

  # FORWARD

  layer.forward(inpt)
  forward_out = layer.output
  print(layer)

  # BACKWARD

  delta = np.zeros(shape=inpt.shape, dtype=float)
  layer.backward(delta)

  # Visualizations

  fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(10, 5))
  fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.15)

  fig.suptitle('L2Normalization Layer')

  ax1.imshow(float_2_img(inpt[0]))
  ax1.set_title('Original image')
  ax1.axis('off')

  ax2.imshow(float_2_img(forward_out[0]))
  ax2.set_title("Forward")
  ax2.axis("off")

  ax3.imshow(float_2_img(delta[0]))
  ax3.set_title('Backward')
  ax3.axis('off')

  fig.tight_layout()
  plt.show()
