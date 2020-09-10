from docs_conf.conf import *

branch = 'latest'
master_doc = 'index'

linkcheck_ignore = [
    'http://localhost',
]

extensions = [
   'sphinxcontrib.redoc',
]

redoc = [
		    {
		        'name': 'OSDF API',
		        'page': 'sections/osdf-api',
		        'spec': './api/swagger/oof-osdf-has-api.json',
		        'embed': True,
		    },
		    {
		        'name': 'OPTENG API',
		        'page': 'sections/opteng-api',
		        'spec': './api/swagger/oof-osdf-has-api.json',
		        'embed': True,
		    }
        ]

redoc_uri = 'https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js'

intersphinx_mapping = {}

html_last_updated_fmt = '%d-%b-%y %H:%M'

def setup(app):
    app.add_stylesheet("css/ribbon.css")
