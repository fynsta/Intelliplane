import { readFileSync } from 'fs';
import { fstat } from 'fs';

/**
 * Radio input frame
 * @typedef {Object} RXFrame
 * @property {number} pcTime
 * @property {number} thr
 * @property {number} ail
 * @property {number} elv
 * 
 */

/**
 * @typedef {Object} GPSFrame
 * @property {number} pcTime
 * @property {number} lat
 * @property {number} lon
 */

/**
 * Basic flight data frame
 * @typedef {Object} BasicFrame
 * @property {number} pcTime
 * @property {number} a - altitude in m
 * @property {number} p - pitch in radians
 * @property {number} b - bank in radians
 * @property {number} s - speed in m/s
 * @property {number} h - heading in radians
 */

/**
 * @typedef {BasicFrame&GPSFrame&RXFrame} Frame
 */
export class DataReader {
    /**@param {string} path */
    constructor(path) {

        const logString = readFileSync(path, { encoding: 'utf-8' });
        /** @type {Frame[]} */
        this.log = JSON.parse(logString);
        const initialTime = this.log[0].pcTime;
        this.log.forEach((frame) => frame.pcTime = (frame.pcTime - initialTime) / 1000);
        this.length = this.log[this.log.length - 1].pcTime;
    }
    /**
     * 
     * @param {number} time - time of the frame to get
     * @returns {Frame}  Frame containing all values at time
     */
    getFrame(time) {
        let minIndex = 0;
        let maxIndex = this.log.length - 1;
        while (minIndex + 1 < maxIndex) {
            let mean = Math.floor((minIndex + maxIndex) / 2);
            if (this.log[mean].pcTime < time) {
                minIndex = mean;
            } else {
                maxIndex = mean;
            }
        }
        const targetFrame = this.log[minIndex];
        /**
         * 
         * @param {number} startIndex 
         * @param {(el:Object)=>boolean} isValid 
         */
        const findFrames = (startIndex, isValid) => {
            let maxFrame;
            for (let testIndex = this.log[startIndex].pcTime >= time ? startIndex : startIndex + 1; testIndex < this.log.length; testIndex++) {
                const toTest = this.log[testIndex];
                if (isValid(toTest)) {
                    maxFrame = toTest;
                    break;
                }
            }

            let minFrame;
            for (let testIndex = startIndex; testIndex >= 0; testIndex--) {
                const toTest = this.log[testIndex];
                if (isValid(toTest)) {
                    minFrame = toTest;
                    break;
                }
            }
            if(!maxFrame){
                return minFrame;
            }else if(!minFrame){
                return maxFrame;
            }else if (maxFrame.pcTime == minFrame.pcTime) {
                return maxFrame;
            }
            const weight = (time - minFrame.pcTime) / (maxFrame.pcTime - minFrame.pcTime);
            /** @type {Frame} */
            const result = {};
            for (let key of Object.keys(minFrame)) {
                result[key] = maxFrame[key] * weight + minFrame[key] * (1 - weight);
            }
            return result;
        };
        const isRx = (el) => el.thr != null;
        const rxFrame = findFrames(minIndex, isRx);
        const isBasic = (el) => el.p != null;
        const basicFrame = findFrames(minIndex, isBasic);
        const isGPS = (el) => el.lat != null;
        const gpsFrame = findFrames(minIndex, isGPS);
        const result = {};
        Object.assign(result, rxFrame, basicFrame, gpsFrame)
        return result;
    }
}