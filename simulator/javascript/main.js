const tf = require('@tensorflow/tfjs');
require('@tensorflow/tfjs-node');
require('./models/basic')
const DataReader = require('./dataReader/dataReader.js');
const reader = new DataReader('/home/olep/Dropbox/Intelliplane/Intelliplane/dataCollection/logs/flight2.txt');
const dataset = reader.toTfDataset(10, 25, 5);
const inputs = tf.data.array(dataset.inputs);
const labels = tf.data.array(dataset.labels);
