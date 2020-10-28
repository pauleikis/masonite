"""Start of Application. This function is the gunicorn server."""

from src.masonite.environment import LoadEnvironment

"""Load Environment Variables
Take environment variables from the .env file and load them in.
"""

LoadEnvironment()


def app(environ, start_response):
    """The WSGI Application Server.

    Arguments:
        environ {dict} -- The WSGI environ dictionary
        start_response {WSGI callable}

    Returns:
        WSGI Response
    """
    from wsgi import container

    """Add Environ To Service Container
    Add the environ to the service container. The environ is generated by the
    the WSGI server above and used by a service provider to manipulate the
    incoming requests
    """

    container.bind('Environ', environ)

    """Execute All Service Providers That Require The WSGI Server
    Run all service provider boot methods if the wsgi attribute is true.
    """

    try:
        for provider in container.make('WSGIProviders'):
            container.resolve(provider.boot)
    except Exception as e:
        container.make('ExceptionHandler').load_exception(e)

    """We Are Ready For Launch
    If we have a solid response and not redirecting then we need to return
    a 200 status code along with the data. If we don't, then we'll have
    to return a 302 redirection to where ever the user would like go
    to next.
    """

    from src.masonite.response import Response


    start_response(container.make('Request').get_status_code(),
                   container.make(Response).get_and_reset_headers())

    """Final Step
    This will take the data variable from the Service Container and return
    it to the WSGI server.
    """
    return iter([container.make('Response')])
