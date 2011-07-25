#!/usr/bin/env python

import torch
import os, sys
import optparse
import math

def NormalizeStdArrayset(arrayset):
  arrayset.load()

  length = arrayset.shape[0]
  n_samples = len(arrayset)
  mean = torch.core.array.float64_1(length)
  std = torch.core.array.float64_1(length)

  mean.fill(0)
  std.fill(0)

  for array in arrayset:
    x = array.get().cast('float64')
    mean += x
    std += (x ** 2)

  mean /= n_samples
  std /= n_samples
  std -= (mean ** 2)
  std = std ** 0.5 # sqrt(std)

  arStd = torch.io.Arrayset()
  for array in arrayset:
    arStd.append(array.get().cast('float64') / std)

  return (arStd,std)


def multiplyVectorsByFactors(matrix, vector):
  for i in range(0, matrix.rows()):
    for j in range(0, matrix.columns()):
      matrix[i, j] *= vector[j]


import fileinput
from optparse import OptionParser

usage = "usage: %prog [options] <input_files> "

parser = OptionParser(usage)
parser.set_description("Train a GMM model")

parser.add_option("-o",
                  "--output-file",
                  dest="output_file",
                  help="Output file",
                  type="string",
                  default="wm.hdf5")
parser.add_option("-g",
                  "--n-gaussians",
                  dest="n_gaussians",
                  help="",
                  type="int",
                  default=5)
parser.add_option("--iterk",
                  dest="iterk",
                  help="Max number of iterations of KMeans",
                  type="int",
                  default=25)
parser.add_option("--iterg",
                  dest="iterg",
                  help="Max number of iterations of GMM",
                  type="int",
                  default=25)
parser.add_option("-e",
                  dest="convergence_threshold",
                  help="End accuracy",
                  type="float",
                  default=1e-05)
parser.add_option("-v",
                  "--variance-threshold",
                  dest="variance_threshold",
                  help="Variance threshold",
                  type="float",
                  default=0.001)
parser.add_option('--no-update-weights',
                  action="store_true",
                  dest="no_update_weights",
                  help="Do not update the weights",
                  default=False)
parser.add_option('--no-update-means',
                  action="store_true",
                  dest="no_update_means",
                  help="Do not update the means",
                  default=False)
parser.add_option('--no-adapt-variances',
                  action="store_true",
                  dest="no_update_variances",
                  help="Do not update the variances",
                  default=False)
parser.add_option("-n",
                  "--no-norm",
                  action="store_true",
                  dest="no_norm",
                  help="Do not normalize input features for KMeans",
                  default=False)
parser.add_option('--self-test',
                  action="store_true",
                  dest="test",
                  help=optparse.SUPPRESS_HELP,
                  default=False)

(options, args) = parser.parse_args()

if options.test:
  if os.path.exists("/tmp/input.hdf5"):
    os.remove("/tmp/input.hdf5")
  
  options.output_file = "/tmp/wm.hdf5"
  arrayset = torch.io.Arrayset()
  array1 = torch.core.array.array([ 0,  1,  2,  3], 'float64')
  arrayset.append(array1)
  array2 = torch.core.array.array([ 3,  1,  5,  2], 'float64')
  arrayset.append(array2)
  array3 = torch.core.array.array([ 6,  7,  2,  5], 'float64')
  arrayset.append(array3)
  array4 = torch.core.array.array([ 3,  6,  2,  3], 'float64')
  arrayset.append(array4)
  array5 = torch.core.array.array([ 9,  8,  6,  4], 'float64')
  arrayset.append(array5)

  options.n_gaussians = 1
  arrayset.save("/tmp/input.hdf5")

  f = open("/tmp/input.lst", 'w')
  f.write("/tmp/input.hdf5\n")
  f.close()
  
  args.append("/tmp/input.lst")


# Read the file list
filelist = []
for line in fileinput.input(args):
  filelist.append(line.rstrip('\r\n'))

# Create an arrayset from the input files
ar = torch.io.Arrayset()
for myfile in filelist:
  myarrayset = torch.io.Arrayset(myfile)
  n_blocks = len(myarrayset)
  for b in range(0,n_blocks):
    x = myarrayset[b].get()
    ar.append(x)

# Compute input size
input_size = ar.shape[0]

# Create a normalized sampler
if options.no_norm:
	normalizedAr = ar
else:
	(normalizedAr,stdAr) = NormalizeStdArrayset(ar)
	
# Create the machines
kmeans = torch.machine.KMeansMachine(options.n_gaussians, input_size)
gmm = torch.machine.GMMMachine(options.n_gaussians, input_size)

# Create the KMeansTrainer
kmeansTrainer = torch.trainer.KMeansTrainer()
kmeansTrainer.convergenceThreshold = options.convergence_threshold
kmeansTrainer.maxIterations = options.iterk

# Train the KMeansTrainer
kmeansTrainer.train(kmeans, normalizedAr)

[variances, weights] = kmeans.getVariancesAndWeightsForEachCluster(normalizedAr)
means = kmeans.means

# Undo normalization
if not options.no_norm:
	multiplyVectorsByFactors(means, stdAr)
	multiplyVectorsByFactors(variances, stdAr ** 2)

# Initialize gmm
gmm.means = means
gmm.variances = variances
gmm.weights = weights
gmm.setVarianceThresholds(options.variance_threshold)

# Train gmm
trainer = torch.trainer.ML_GMMTrainer(not options.no_update_means, not options.no_update_variances, not options.no_update_weights)
trainer.convergenceThreshold = options.convergence_threshold
trainer.maxIterations = options.iterg
trainer.train(gmm, ar)

# Save gmm
config = torch.io.HDF5File(options.output_file)
gmm.save(config)

if options.test:
  os.remove("/tmp/input.hdf5")
  os.remove("/tmp/input.lst")
  
  if not os.path.exists("/tmp/wm.hdf5"):
    sys.exit(1)
  else:
    os.remove("/tmp/wm.hdf5")
