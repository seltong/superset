from flask.sessions import SecureCookieSessionInterface
from flask import request, current_app

class CustomSessionInterface(SecureCookieSessionInterface):
    """
    A custom session interface that uses a different cookie name for
    embedded routes. If the request path starts with '/embedded', it uses
    'embedded_session' instead of the default cookie name.
    """

    def _get_cookie_name(self, app):
        # Decide which cookie name to use based on the request path.
        if request.path.startswith("/embedded"):
            return "embedded_session"
        else:
            # Use the app configuration value or fallback to "session"
            return app.config.get("SESSION_COOKIE_NAME", "session")

    def open_session(self, app, request):
        cookie_name = self._get_cookie_name(app)
        val = request.cookies.get(cookie_name)
        if not val:
            return self.session_class()
        try:
            data = self.get_signing_serializer(app).loads(val)
            return self.session_class(data)
        except Exception:
            return self.session_class()

    def save_session(self, app, session, response):
        cookie_name = self._get_cookie_name(app)
        # If session is empty, delete cookie if modified
        if not session:
            if session.modified:
                response.delete_cookie(
                    cookie_name,
                    domain=self.get_cookie_domain(app),
                    path=self.get_cookie_path(app),
                )
            return

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        secure = self.get_cookie_secure(app)
        httponly = self.get_cookie_httponly(app)
        samesite = self.get_cookie_samesite(app)
        expires = self.get_expiration_time(app, session)
        val = self.get_signing_serializer(app).dumps(dict(session))
        response.set_cookie(
            cookie_name,
            val,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            samesite=samesite,
        )
