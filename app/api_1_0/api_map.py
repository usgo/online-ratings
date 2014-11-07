from flask import current_app, jsonify, url_for
from . import api


@api.route('/')
def api_list():
    '''return a json list of api endpoints'''
    urls = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint is not 'static' and rule.endpoint.startswith('api.'):
            options = {}
            for arg in rule.arguments:
                options[arg] = "[{0}]".format(arg)

            urls[rule.endpoint] = {
                'methods': ','.join(rule.methods),
                'url': url_for(rule.endpoint, **options)
            }
    return jsonify(urls)
