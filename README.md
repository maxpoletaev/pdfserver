# PDF Server

Service that lets you create PDF documents from HTML files or webpages with Google Chrome and simple HTTP interface.

## API

Start the service with Docker:

```
docker run -d --name pdf-service -p 8000:8000 --cap-add=SYS_ADMIN zenwalker/pdfserver
```

Now you can use the HTTP interface to generate PDF from any URL:

```
curl http://localhost:8000/?url=https://github.com -o output.pdf
```

Also you can pass a HTML document as a string:

```
curl http://localhost:8000 -d '<h1>It works!</h1>' -o output.pdf
```

Additional print arguments such as `scale` or `landscape` could be passed with GET parameters:

```
curl http://localhost:8000/?scale=2&landscape=true&url=https://github.com -o output.pdf
```

The full list of available arguments can be found at [Chrome DevTool Protocol Documentation](https://chromedevtools.github.io/devtools-protocol/tot/Page#method-printToPDF).

Thanks [pychrome](https://github.com/fate0/pychrome) for providing a great Python wrapper of Chrome DevTool API.
