const tf = require('@tensorflow/tfjs');

const cast=tf.customGrad((x,save)=>{
    return {
        value: tf.cast(x, 'int32'),
        gradFunc: (dy,saved)=>tf.zeros(x.shape)
    };
});
const gather=tf.customGrad((x,save)=>{
    return {
        value: tf.gather(y_ref, intFloorIndices, 1),
        gradFunc: (dy,saved)=>tf.zeros(x.shape)
    };
});

/**
 * 
 * @param {tf.Tensor} x 
 * @param {tf.Tensor} r_ref_min 
 * @param {tf.Tensor} x_ref_max 
 * @param {tf.Tensor} y_ref 
 */
function linInterpolation(x, x_ref_min, x_ref_max, y_ref) {
    const delta = tf.sub(x_ref_max, x_ref_min);
    let transformedIndices = tf.div(tf.sub(x, x_ref_min), delta);
    transformedIndices = tf.mul(transformedIndices, y_ref.shape[1]);
    const floorIndices = tf.floor(transformedIndices);
    const intFloorIndices =cast(floorIndices); //tf.cast(floorIndices, 'int32');
    const intCeilIndices = tf.add(intFloorIndices, tf.scalar(1, 'int32'));
    const minValues = tf.gather(y_ref, intFloorIndices, 1);
    const maxValues = tf.gather(y_ref, intCeilIndices, 1);
    const dif = tf.sub(maxValues, minValues);
    const proportion = tf.sub(transformedIndices, floorIndices);
    const summand = tf.mul(proportion, dif);
    const result = tf.add(minValues, summand);
    return result;
}
module.exports = linInterpolation;
tf.load_