import * as tf from '@tensorflow/tfjs';
import {DataReader} from './dataReader/dataReader.js';
const reader =new DataReader('/home/olep/Dropbox/Intelliplane/Intelliplane/dataCollection/logs/flight2.txt');
dataset=reader.toTfDataset(10,25,5);