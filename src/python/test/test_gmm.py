#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri 16 Jul 2010 09:30:53 CEST

"""Tests cropping features
"""

import os, sys
import unittest
import torch

def compare(v1, v2, width):
  return abs(v1-v2) <= width

class GmmTest(unittest.TestCase):
  """Performs various tests for the Torch::ipGeomNorm object."""

  ###############################################################
  #

  def test_load_and_construct_01(self):
    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution()
    status = gmm.loadFile("does.not.exist.gmm")
    self.assertFalse(status)

  def test_load_and_construct_02(self):
    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution()
    status = gmm.loadFile("data_machine/1001.gmm")
    self.assertTrue(status)

  def test_load_and_construct_03(self):
    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution("data_machine/1001.gmm")
    self.assertTrue(True) # bad need to find a good test here


  ###############################################################
  #

  def test_score_01(self):
    zero_tensor = torch.core.DoubleTensor(91)
    zero_tensor.fill(0)
    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution("data_machine/1001.gmm")

    score = gmm.score(zero_tensor)
    self.assertTrue(compare(score, -15.3702381398, 1e-6))
 
  # same score but different load
  def test_score_02(self):
    zero_tensor = torch.core.DoubleTensor(91)
    zero_tensor.fill(0)

    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution()
    gmm.loadFile("data_machine/1001.gmm")

    score = gmm.score(zero_tensor)
    self.assertTrue(compare(score, -15.3702381398, 1e-6))

  def test_score_03(self):
    zero_tensor = torch.core.DoubleTensor(91)
    zero_tensor.fill(0)

    gmm = torch.machine.MultiVariateDiagonalGaussianDistribution("data_machine/1046.gmm")

    score = gmm.score(zero_tensor)
    self.assertTrue(compare(score, -14.6556824302, 1e-6))

if __name__ == '__main__':
  sys.argv.append('-v')
  os.chdir(os.path.realpath(os.path.dirname(sys.argv[0])))
  unittest.main()

