const tf = require('@tensorflow/tfjs');
const linInt = require('../tools/linearInterpolation');
input = tf.layers.input({ shape: [null, 25, 9] });
let indices = [[1.3, 2.4]];
indices = tf.tensor(indices);
const f = (indices) => {
    let values = [[...Array(10).keys()].map(el => el * el)];
    values = tf.tensor(values);
    const result = linInt(indices, tf.tensor(1.1), tf.tensor(5), values);
    return result;
};
const fs=tf.grad(f);
const result=fs(indices);
array = result.arraySync();
class MyCell extends tf.layers.RNNCell {
    
}