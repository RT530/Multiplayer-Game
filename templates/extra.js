Array.prototype.swap = function (a, b) {
    var a_b = this[a]
    var b_a = this[b]

    this[a] = b_a
    this[b] = a_b
}

Array.prototype.upset = function () {
    var list = []
    for (var i = 0; i < this.length; i++)list.push(this[i])

    var number = 0
    while (number != this.length) {
        number = 0
        var a = Math.floor(Math.random() * this.length)
        var b = Math.floor(Math.random() * this.length)
        this.swap(a, b)

        for (var i = 0; i < this.length; i++) if (this[i] != list[i]) number++
    }
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

Array.prototype.min = function (key) {
    var min = 1000000000000000
    if (key) {
        for (var i = 0; i < this.length; i++)if (this[i][key] && this[i][key] < min) min = this[i][key]
    } else {
        for (var i = 0; i < this.length; i++)if (this[i] < min) min = this[i]
    }
    return min
}

Array.prototype.delete = function (number) {
    this.splice(number, 1)
}

Array.prototype.delete_element = function (element) {
    if (this.indexOf(element) == -1) return
    while (this.indexOf(element) != -1) this.delete(this.indexOf(element))
}

Array.prototype.add = function (key) {
    var number = 0
    if (key) {
        for (var i = 0; i < this.length; i++)if (this[i][key]) number += this[i][key]
    } else {
        for (var i = 0; i < this.length; i++)number += this[i]
    }
    return number
}

String.prototype.replaceAll = function (find, replace) {
    return this.replace(new RegExp(find, 'g'), replace)
}

String.prototype.find = function (find) {
    var number = 0
    var text = this
    for (var i = 0; i < text.length; i++) {
        if (text[i] == find) number++
    }
    return number
}

String.prototype.instert = function (text, pos) {
    return this.slice(0, pos) + text + this.slice(pos)
}

Date.prototype.format = function (format) {
    var time = {
        D: this.getDate(),
        h: this.getHours(),
        s: this.getSeconds(),
        m: this.getMinutes(),
        Y: this.getFullYear(),
        M: this.getMonth() + 1
    }

    var text = ''
    for (var i = 0; i < format.length; i++) {
        if (time[format[i]] || time[format[i]] == 0) {
            if (`${time[format[i]]}`.length < 2) time[format[i]] = '0' + time[format[i]]
            text += time[format[i]]
        } else {
            text += format[i]
        }
    }

    return text
}

Math.radian = function (degree) {
    return degree * Math.PI / 180
}

Math.degree = function (radian) {
    return radian * 180 / Math.PI
}

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

$.fn.tree = function (json, open) {
    for (var i = 0; i < json.length; i++) {
        if (json[i]['id']) {
            var id = json[i]['id']
        } else {
            var id = json[i]['title'].replaceAll(' ', '_').replaceAll('-', '_')
            while (id.indexOf('.') != -1) id = id.replace('.', '-')

            if ($(this).attr('id') == undefined) {
                id = `${$(this)[0].tagName}-${id}`
            } else {
                id = `${$(this).attr('id').replace('-block', '')}-${id}`
            }
        }

        if ($(this).attr('title') == undefined) {
            var title = json[i]['title']
        } else {
            var title = `${$(this).attr('title')}/${json[i]['title']}`
        }

        if (json[i]['file']) {
            $(this).append(`
                <span id="${id}" title="${title}" style="display: inline-block;">
                    <img id="${id}-img" src="/static/filemin/close folder.png" height="25">
                    <span id="${id}-text" title="${title}" style="display: inline-block; font-size: 16px;">&nbsp${json[i]['title']}</span>
                </span>
                <br>
            `)
            $(`#${id}`).width(json[i]['title'].length * 8 + 100)
            if (json[i]['file'].length > 0) {
                $(this).append(`<ul id="${id}-block" title="${title}" style="display: none;"></ul>`)
                $(`#${id}-block`).tree(json[i]['file'], open)
            }
        } else {
            $(this).append(`
                <li title="${title}" style="list-style-type: none; white-space: nowrap;">
                    <img src="/static/filemin/file.png" height="25">
                    <span id="${id}-text">${json[i]['title']}</span>
                </li>
            `)
        }

        if (open) {
            title = title.split('/')
            var match_number = match(open.split('/'), title)
            if (match_number == title.length) {
                if (match_number == open.split('/').length) {
                    $(`#${id}-text`).css('background-color', '#007bff')
                    $(`#${id}-text`).css('color', '#ffffff')
                }
                $(`#${id}-img`).attr('src', '/static/filemin/open folder.png')
                $(`#${id}-block`).show()
            }
        }
    }
}

function match(a, b) {
    var number = 0
    for (var i = 0; i < [a.length, b.length].min(); i++) {
        if (a[i] == '*' || b[i] == '*' || a[i] == b[i]) number++
    }
    return number
}

function rgb(r, g, b) {
    r *= 1
    g *= 1
    b *= 1

    r = r.toString(16)
    g = g.toString(16)
    b = b.toString(16)

    if (r.length != 2) r = '0' + r
    if (g.length != 2) g = '0' + g
    if (b.length != 2) b = '0' + b

    return '#' + r + g + b
}

function decode_rgb(color) {
    if (color[0] == '#') color = color.substr(1)
    if (color.length != 6) return

    return {
        r: parseInt(color[0] + color[1], 16),
        g: parseInt(color[2] + color[3], 16),
        b: parseInt(color[4] + color[5], 16)
    }
}

function reverse_rgb(color) {
    var rgb = decode_rgb(color)

    var r = 255 - rgb.r
    var g = 255 - rgb.g
    var b = 255 - rgb.b

    return rgb(r, g, b)
}

function get_request() {
    var request = {}
    var search = location.search
    if (search.indexOf('?') != -1) {
        search = search.substr(1)
        search = search.split("&")
        for (var i = 0; i < search.length; i++) {
            request[search[i].split('=')[0]] = unescape(search[i].split('=')[1])
        }
    }
    return request
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

function get_code() {
    code = []
    text = 'abcdefghij'
    time = `${Date.now()}`
    for (var i = 0; i < time.length; i++) {
        code.push(text[time[i] * 1])
        if (Math.random() < 0.5) code[code.length - 1] = code[code.length - 1].toUpperCase()
    }
    return code.join('')
}

function is_mobile() {
    var mobile = ['Android', 'iPhone', 'SymbianOS', 'Windows Phone', 'iPad', 'iPod'];

    for (var i = 0; i < mobile.length; i++) {
        if (navigator.userAgent.indexOf(mobile[i]) != -1) return true
    }

    return false
}

function remove_characters(input_text, replace, extra) {
    if (!replace) replace = ''
    if (extra) input_text = remove_characters(input_text, replace)

    var characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for (var i = 0; i < characters.length; i++) {
        var character = characters[i]
        while (input_text.indexOf(character) != -1) {
            input_text = input_text.replace(character, replace)
        }
    }

    return input_text
}

function get_distance(x1, y1, x2, y2) {
    return Math.abs(Math.sqrt(Math.pow(x1 - x2, 2) + Math.pow(y1 - y2, 2)))
}