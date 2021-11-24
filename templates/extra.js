//this file have the function I often use

$.fn.center = function (mode) {
    if (mode == 'css') {
        var height = ($(window).height() - get_number($(this).css('height'))) / 2
        var width = ($(window).width() - get_number($(this).css('width'))) / 2
    } else {
        var height = ($(window).height() - $(this).height()) / 2
        var width = ($(window).width() - $(this).width()) / 2
    }

    $(this).css({
        top: height,
        left: width,
        position: 'absolute'
    })
}

function get_number(text) {
    var number = ''
    for (var i = 0; i < text.length; i++)
        if (!isNaN(text[i] * 1) || text[i] == '.')
            if (number.indexOf('.') == -1)
                number += text[i]
            else
                break
    return number * 1
}

Array.prototype.max = function (key) {
    var max = -100000000000000
    if (key) {
        for (var i = 0; i < this.length; i++) if (this[i][key] > max) max = this[i][key]
    } else {
        for (var i = 0; i < this.length; i++)if (this[i] > max) max = this[i]
    }
    return max
}

Math.degree = function (radian) {
    return radian * 180 / Math.PI
}

Math.radian = function (degree) {
    return degree * Math.PI / 180
}