function year(date = 0) {

    const year = date % 100;
    return year + 2000;
}

function month(date = 0) {

    return Math.floor((date / 100) % 100);
}

function day(date = 0) {

    return Math.floor(date / 10000);
}

function hour(time = 0) {

    return Math.floor(time / 1000000);
}

function minute(time = 0) {

    return Math.floor((time / 10000) % 100);
}

function second(time = 0) {

    return Math.floor((time / 100) % 100);
}

function centisecond(time = 0) {

    return time % 100;
}
function timeToString(time) {
    return hour(time) + ":" + minute(time) + ":" + second(time);
}