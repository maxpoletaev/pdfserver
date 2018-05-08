from tempfile import NamedTemporaryFile
from contextlib import contextmanager
import subprocess
import base64
import time
import os

from flask import Flask, Response, request
import pychrome

from .schemas import print_params_schema, validate_schema

app = Flask(__name__)
browser = pychrome.Browser(url='http://127.0.0.1:9222')

CHROME_BIN = os.environ.get('CHROME_BIN', 'google-chrome')
chrome = subprocess.Popen([
    CHROME_BIN,
    '--headless',
    '--disable-gpu',
    '--remote-debugging-port=9222'
])


@contextmanager
def open_tab(url, timeout=None):
    tab = browser.new_tab()
    tab.start()

    waiting = True

    def page_loaded(timestamp):
        nonlocal waiting
        waiting = False

    tab.Page.enable()
    tab.Page.navigate(url=url, _timeout=timeout)
    tab.Page.loadEventFired = page_loaded

    while waiting:
        time.sleep(1)

    yield tab
    tab.stop()
    browser.close_tab(tab)


def url_to_pdf(url, print_params):
    with open_tab(url, timeout=10) as tab:
        chrome_response = tab.Page.printToPDF(**print_params)
        return base64.b64decode(chrome_response['data'])


def html_to_pdf(html, print_params):
    html_file = NamedTemporaryFile(suffix='.html')
    html_file.write(html)
    html_file.seek(0)

    with open_tab('file://' + html_file.name, timeout=10) as tab:
        chrome_response = tab.Page.printToPDF(**print_params)
        pdf_content = base64.b64decode(chrome_response['data'])

    html_file.close()
    return pdf_content


@app.route('/', methods=['GET', 'POST'])
def print_to_pdf():
    request_args = request.args.to_dict()
    url = request_args.pop('url', None)
    print_params = validate_schema(print_params_schema, request_args)

    if url:
        pdf_content = url_to_pdf(url, print_params)
        return Response(pdf_content, content_type='application/pdf')

    if request.method == 'POST':
        data = request.get_data()
        pdf_content = html_to_pdf(data, print_params)
        return Response(pdf_content, content_type='application/pdf')

    return Response()
