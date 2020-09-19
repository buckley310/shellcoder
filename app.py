#!/usr/bin/env python3

import os
import subprocess
import json
from tempfile import NamedTemporaryFile
from flask import Flask, request, send_file

app = Flask(__name__)


@app.route('/')
def index():
    return send_file('index.html')


@app.route('/dasm', methods=['POST'])
def ndisasm():
    j = json.loads(request.data.decode())
    bits = str(int(j['bits']))
    hexonly = ''.join(filter(
        "0123456789abcdef".__contains__,
        j['code'].lower()
    ))

    if len(hexonly) % 2:
        return "Invalid Input"

    with NamedTemporaryFile() as f:
        f.write(bytes.fromhex(hexonly))
        f.flush()

        res = b''
        res += subprocess.check_output(('ndisasm', f.name, '-b', bits),
                                       stderr=subprocess.STDOUT)

        res += b'\n'
        for x in range(len(hexonly)//2):
            res += b'\\x' + hexonly[2*x:2*x+2].encode()

        return res


@app.route('/asm', methods=['POST'])
def nasm():
    j = json.loads(request.data.decode())
    bits = str(int(j['bits']))

    with NamedTemporaryFile(mode='w') as fa:
        with NamedTemporaryFile(mode='wb+') as fb:
            fa.write(f'BITS {bits}\n')
            fa.write(j['code'])
            fa.flush()

            fb.flush()
            res = b''
            res += subprocess.check_output(['nasm', fa.name, '-o', fb.name],
                                           stderr=subprocess.STDOUT)

            res += subprocess.check_output(['ndisasm', fb.name, '-b', bits],
                                           stderr=subprocess.STDOUT)

            hexcode = ''.join(['\\x'+('0'+hex(c)[2:])[-2:] for c in fb.read()])
            res += b'\n' + hexcode.encode()
            return res


if __name__ == '__main__':
    app.run()
