from secrets import token_bytes


def encode_file(file, key=None):
    text = open(file, encoding='utf-8').read().encode('utf-8')
    text_code = int.from_bytes(text, 'big')
    if key is None:
        key = int.from_bytes(token_bytes(len(text)), 'big')
        open(f"{file.split('.')[0]}.key", 'wb').write(key.to_bytes(len(str(key)), 'big'))
    else:
        key = int.from_bytes(open(key, 'rb').read(), 'big')
    code = text_code ^ key

    open(file, 'wb').write(code.to_bytes(len(str(code)), 'big'))


def decode_file(file_name, key=None):
    if key is None:
        key = int.from_bytes(open(f"{file_name.split('.')[0]}.key", 'rb').read(), 'big')
    else:
        key = int.from_bytes(open(key, 'rb').read(), 'big')
    file = int.from_bytes(open(file_name, 'rb').read(), 'big')
    text = file ^ key
    length = (text.bit_length() + 7) // 8
    text = int.to_bytes(text, length, 'big').decode('utf-8')

    return text
