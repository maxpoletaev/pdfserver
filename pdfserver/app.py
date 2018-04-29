from tempfile import NamedTemporaryFile
from contextlib import contextmanager
import subprocess
import base64
import time
import os

from flask import Flask, Response, request
import pychrome

app = Flask(__name__)
CHROME_BIN = os.environ.get('CHROME_BIN', 'google-chrome')

chrome = subprocess.Popen([
    CHROME_BIN,
    '--headless',
    '--disable-gpu',
    '--remote-debugging-port=9222'
])

browser = pychrome.Browser(url='http://127.0.0.1:9222')


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


def url_to_pdf(url):
    with open_tab(url, timeout=10) as tab:
        chrome_response = tab.Page.printToPDF(printBackground=True)
        pdf_content = base64.b64decode(chrome_response['data'])

    response = Response(pdf_content, content_type='application/pdf')
    return response


def html_to_pdf(html):
    html_file = NamedTemporaryFile(suffix='.html')
    html_file.write(html)
    html_file.seek(0)

    with open_tab('file://' + html_file.name, timeout=10) as tab:
        chrome_response = tab.Page.printToPDF(printBackground=True)
        pdf_content = base64.b64decode(chrome_response['data'])

    html_file.close()
    response = Response(pdf_content, content_type='application/pdf')
    return response


@app.route('/', methods=['GET', 'POST'])
def print_to_pdf():
    if request.method == 'POST':
        data = request.get_data()
        return html_to_pdf(data)

    if request.args.get('url'):
        return url_to_pdf(request.args['url'])

    return Response()
