const tf = require('@tensorflow/tfjs');
require('@tensorflow/tfjs-node');
const DataReader=require('./dataReader/dataReader.js');
const reader =new DataReader('/home/olep/Dropbox/Intelliplane/Intelliplane/dataCollection/logs/flight2.txt');
dataset=reader.toTfDataset(10,25,5);
console.log(tf.Abs());