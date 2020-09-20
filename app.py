#!/usr/bin/env python3

import os
import subprocess
import webbrowser
import json
from tempfile import NamedTemporaryFile, TemporaryDirectory
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

        res = subprocess.run(
            ('ndisasm', f.name, '-b', bits),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        ).stdout

        res += b'\n'
        for x in range(len(hexonly)//2):
            res += b'\\x' + hexonly[2*x:2*x+2].encode()

        return res


@app.route('/asm', methods=['POST'])
def nasm():
    j = json.loads(request.data.decode())
    bits = str(int(j['bits']))

    with NamedTemporaryFile(mode='w') as f:
        with TemporaryDirectory() as d:
            f.write(f'BITS {bits}\n')
            f.write(j['code'])
            f.flush()

            res = subprocess.run(
                ['nasm', f.name, '-o', d+'/a'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ).stdout

            res += subprocess.run(
                ['ndisasm', d+'/a', '-b', bits],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ).stdout

            if os.path.exists(d+'/a'):
                with open(d+'/a', 'rb') as f2:
                    hexchars = ['\\x'+('0'+hex(c)[2:])[-2:] for c in f2.read()]
                res += b'\n' + ''.join(hexchars).encode()
            return res


if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000')
    app.run()
