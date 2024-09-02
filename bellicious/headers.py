from flask import Response, request
from flask import render_template

def render_with_headers(template_name, mime_type='text/html', allow_scripts=False, **kwargs):
    if 'application/xhtml+xml' in request.headers.get('Accept', ''):
        # Client header is set and explicitly declares XHTML parser support.
        mime_type = 'application/xhtml+xml; charset=UTF-8'

    # Render the template
    content = render_template(template_name, **kwargs)

    # Adjust CSP headers if scripts are allowed
    if allow_scripts:
        csp_header = "default-src 'self';"
    else:
        csp_header = "default-src 'self'; script-src 'none';"

    headers = {
        'Content-Security-Policy': csp_header
    }

    return Response(content, content_type=mime_type, headers=headers)
