caffe_root = '/home/nico/caffe-build_3_apr_2015/'
import sys
sys.path.insert(0,caffe_root+'python')
import caffe
import numpy as np
from pylab import *
import glob
import pickle
import os
#path = "/home/nico/DepthPrediction/train_1/"
#in this normalization, I set the origin to the furthest point 
def normalise_x(x):
    return np.abs(x-320.0)/32.0
def normalise_y(y):
    return y/480.0
    return np.abs(y-130)/35.0

'''
with open("/home/nico/DepthPrediction/xy_extension/images_train.txt") as F1:
    images = F1.read().splitlines()
'''
with open("/home/nico/DepthPrediction/xy_extension/label_train.txt") as F2:
    label = F2.read().splitlines()
with open("/home/nico/DepthPrediction/xy_extension/x_train.txt") as F3:
    x = F3.read().splitlines()
with open("/home/nico/DepthPrediction/xy_extension/y_train.txt") as F4:
    y = F4.read().splitlines()
    
caffe.set_device(2)
caffe.set_mode_gpu()
solver = caffe.SGDSolver("/home/nico/DepthPrediction/xy_extension/models/basic_xy/solver_basic_xy.prototxt")
solver.net.copy_from("/home/nico/DepthPrediction/models/unary_depth_regressor/places205CNN_iter_300000_upgraded.caffemodel")

transformer = caffe.io.Transformer({'data': solver.net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load('/home/nico/DepthPrediction/mean.npy')) # mean pixel
transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

num_dbims = len(label)
it = 30000
train_loss = np.zeros(it)
for i in range(0,it):
    ims = np.zeros((128,3,227,227),dtype = np.float32)
    bat_label = np.zeros((128,1,1,1),dtype = np.float32)
    xy = np.zeros((128,1,6,6),dtype = np.float32)
    
    for j in range(128):
        randseed = (num_dbims-1)
        marker = randint(0,randseed)
        bat_label[j] = float(label[marker])
        xy[j][0][0][0] = normalise_x(float(x[marker]))
        xy[j][0][0][1] = normalise_y(float(y[marker]))
    
    #solver.net.blobs['data'].data[...] = ims.transpose(0,3,1,2)
    solver.net.blobs['data'].data[...] = ims
    solver.net.blobs['label'].data[...] = bat_label
    solver.net.blobs['xy'].data[...] = xy
    solver.step(1)
    train_loss[i] = solver.net.blobs['loss'].data
    
    if(i%500 == 0):
        f = open('/home/nico/DepthPrediction/xy_extension/basic_xy/train_loss_record/loss_'+str(i)+'.npy','a')
        np.save(f,train_loss)
        f.close()
        
'''        
with open("/home/nico/DepthPrediction/xy_extension/images_test.txt") as F5:
    images_validation = F5.read().splitlines()
'''
with open("/home/nico/DepthPrediction/xy_extension/label_test.txt") as F6:
    label_validation = F6.read().splitlines()
with open("/home/nico/DepthPrediction/xy_extension/x_test.txt") as F7:
    x_validation = F7.read().splitlines()
with open("/home/nico/DepthPrediction/xy_extension/y_test.txt") as F8:
    y_validation = F8.read().splitlines()

validate_num_dbims = len(label_validation)
validate_loss = np.zeros(100)
for i in range(1,101):
    caffe.set_device(2)
    caffe.set_mode_gpu()
    solver = caffe.SGDSolver("/home/nico/DepthPrediction/xy_extension/models/basic_xy/solver_basic_xy.prototxt")
    solver.net.copy_from("/home/nico/DepthPrediction/xy_extension/models/snapshot_basic_xy/_iter_"+str(i*500)+".caffemodel")
    transformer = caffe.io.Transformer({'data': solver.net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_mean('data', np.load('/home/nico/DepthPrediction/mean.npy')) # mean pixel
    transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
    
    bat_loss = np.zeros(200)
    for j in range(200):
        validate_img = np.zeros((128,3,227,227),dtype=np.float32)
        validate_bat_label = np.zeros((128,1,1,1),dtype=np.float32)
        validate_xy = np.zeros((128,1,6,6),dtype = np.float32)

        for k in range(128):
            validate_randseed = (validate_num_dbims - 1)
            validate_marker = randint(0,validate_randseed)
            validate_bat_label[k] = float(label_validation[validate_marker])
            validate_xy[k][0][0][0] = normalise_x(float(x_validation[validate_marker]))
            validate_xy[k][0][0][1] = normalise_y(float(y_validation[validate_marker]))

        solver.net.blobs['data'].data[...] = validate_img
        solver.net.blobs['label'].data[...] = validate_bat_label
        solver.net.blobs['xy'].data[...] = validate_xy
        out = solver.net.forward()
        bat_loss[j] = out['loss']
        print "processing "+ str(j)
        print "in "+str(i*500)+"th model"
    validate_loss[i-1] = np.mean(bat_loss)
    print "processing " + str(i)
    
    
    f = open('/home/nico/DepthPrediction/xy_extension/basic_xy/validate_loss_record/loss_'+str(i*500)+'.npy','a')
    np.save(f,validate_loss)
    f.close()        
