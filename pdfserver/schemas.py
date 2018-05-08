from voluptuous import Schema, Coerce, Optional, Boolean, MultipleInvalid
from flask import jsonify, abort


# Schema represets Page.PrintToPDF method from Chrome DevTools API.
# https://chromedevtools.github.io/devtools-protocol/tot/Page#method-printToPDF
print_params_schema = Schema({
    Optional('printBackground', default=True): Boolean(),
    'ignoreInvalidPageRanges': Boolean(),
    'displayHeaderFooter': Boolean(),
    'preferCSSPageSize': Boolean(),
    'landscape': Boolean(),
    'scale': Coerce(float),
    'paperWidth': Coerce(float),
    'paperHeight': Coerce(float),
    'marginTop': Coerce(float),
    'marginBottom': Coerce(float),
    'marginLeft': Coerce(float),
    'marginRight': Coerce(float),
    'pageRanges': str,
    'headerTemplate': str,
    'footerTemplate': str,
})


def validate_schema(schema, data):
    try:
        validated_data = schema(data)
    except MultipleInvalid as e:
        errors = {'.'.join(str(x) for x in e.path): e.msg for e in e.errors}
        abort(jsonify(errors))

    return validated_data
