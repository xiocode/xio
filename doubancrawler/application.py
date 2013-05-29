#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Tony.Shao'

from flask import Flask

app = Flask(__name__)
@app.route('/callback')
def index():
    return 'NIMEI'

if __name__ == '__main__':
    app.run(port=80, debug=True)