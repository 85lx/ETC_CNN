import json
import random
from binascii import  hexlify,unhexlify
import numpy as np
import tensorflow as tf
from load_map import Load_map

CLASS_NUM = 6
dict = {0:'chat',1:'email',2:'ft',3:'p2p',4:'stream',5:'voip'}

#log_dir = '/tf/logs/xl_analyser/'
log_dir = './'

X_H = 50
X_W = 76

load_map = Load_map()
(x_data,y_data) = load_map.load_data('../data/data.json')
X_data = np.array(x_data,float)
Y_data = np.array(y_data)
    
Y_data = Y_data.reshape(-1,1)
from sklearn.preprocessing import OneHotEncoder
Y = OneHotEncoder().fit_transform(Y_data).todense()
X = X_data.reshape(-1,X_H,X_W,1)
batch_size = 64

def generatebatch(X,Y,n_exmples,batch_size):
    for batch_i in range(n_exmples // batch_size):
        start = batch_i * batch_size
        end = start + batch_size
        batch_xs = X[start:end]
        batch_ys = Y[start:end]
        yield batch_xs,batch_ys

def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return -1

tf.reset_default_graph()    
tf_X = tf.placeholder(tf.float32,[None,50,76,1],'tf_X')
tf_Y = tf.placeholder(tf.float32,[None,CLASS_NUM],'tf_Y')


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape = shape)
    return tf.Variable(initial)

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

w_conv1 = weight_variable([3, 3, 1, 32])
b_conv1 = bias_variable([32])
#tf.summary.scalar('w_conv1',w_conv1)
tf.summary.histogram('histogram_w1', w_conv1)

h_conv1 = tf.nn.relu(conv2d(tf_X, w_conv1) + b_conv1)

h_pool1 = max_pool_2x2(h_conv1)

w_conv2 = weight_variable([3, 3, 32, 64])
b_conv2 = bias_variable([64])
#tf.summary.scalar('w_conv2',w_conv2)
tf.summary.histogram('histogram_w2', w_conv2)
h_conv2 = tf.nn.relu(conv2d(h_pool1, w_conv2) + b_conv2)

batch_mean2, batch_var2 = tf.nn.moments(h_conv2, [0, 1, 2], keep_dims=True)
shift2 = tf.Variable(tf.zeros([64]))
scale2 = tf.Variable(tf.ones([64]))
epsilon2 = 1e-3
BN_out2 = tf.nn.batch_normalization(h_conv2, batch_mean2, batch_var2, shift2, scale2, epsilon2)
h_pool2 = max_pool_2x2(BN_out2)

print(h_pool2)
w_fc1 = weight_variable([13*19*64, 1024])
b_fc1 = bias_variable([1024])

h_pool2_flat = tf.reshape(h_pool2, [-1, 13*19*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, w_fc1) + b_fc1)

keep_prob = tf.placeholder("float")
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

w_fc2 = weight_variable([1024, CLASS_NUM])
b_fc2 = bias_variable([CLASS_NUM])

y_conv = tf.nn.softmax(tf.matmul(h_fc1_drop, w_fc2) + b_fc2)

tf.add_to_collection('network-output', y_conv)

loss = -tf.reduce_mean(tf_Y*tf.log(tf.clip_by_value(y_conv,1e-11,1.0)))
tf.summary.scalar('entropy_loss',loss)

train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)

predict_label = tf.argmax(y_conv,1)
label_p,idx_p,count_p = tf.unique_with_counts(predict_label)

actual_label = tf.argmax(tf_Y,1)
label,idx,count = tf.unique_with_counts(actual_label)

correct_prediction = tf.equal(actual_label,predict_label)
accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
tf.summary.scalar('accuracy',accuracy)
correct_label = tf.boolean_mask(actual_label,correct_prediction)
label_c,idx_c,count_c=tf.unique_with_counts(correct_label)

merged = tf.summary.merge_all()

#test_writer = tf.summary.FileWriter(log_dir + '/test')

saver = tf.train.Saver()
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.7)  
config = tf.ConfigProto(log_device_placement=False,gpu_options=gpu_options)
config.gpu_options.allow_growth = True
with tf.Session(config=config) as sess:
    sess.run(tf.global_variables_initializer())
    train_writer = tf.summary.FileWriter(log_dir + '/train', sess.graph)
    for epoch in range(3001):
        for batch_xs,batch_ys in generatebatch(X,Y,Y.shape[0],batch_size): 
            sess.run(train_step,feed_dict={tf_X:batch_xs,tf_Y:batch_ys,keep_prob:0.5})
        res = sess.run(accuracy,feed_dict={tf_X:X,tf_Y:Y,keep_prob:1.0})
        if epoch %20 == 0:
            summary = sess.run(merged, feed_dict={tf_X:X,tf_Y:Y,keep_prob:1.0})
            train_writer.add_summary(summary, epoch)
            print (epoch,res)
   
    #res_ypred = predict_label.eval(feed_dict={tf_X:X,tf_Y:Y}).flatten()
    label,count,label_p,count_p,label_c,count_c,acc = \
    sess.run([label,count,label_p,count_p,label_c,count_c,accuracy],feed_dict={tf_X:X,tf_Y:Y,keep_prob:1.0})
    acc_list = []
    for i in range(CLASS_NUM):
        n1 = find_element_in_list(i,label.tolist())
        count_actual = count[n1]
        n2 = find_element_in_list(i,label_c.tolist())
        count_correct = count_c[n2] if n2>-1 else 0
        n3 = find_element_in_list(i,label_p.tolist())
        count_predict = count_p[n3] if n3>-1 else 0
        recall = float(count_correct)/float(count_actual)
        precision = float(count_correct)/float(count_predict) if count_predict>0 else -1
        acc_list.append([dict[i],count_actual,count_correct,count_predict,str(recall),str(precision)])
    print(acc)   
    for item in acc_list:
        print(item)
    
    saver.save(sess,"save/model.ckpt")
