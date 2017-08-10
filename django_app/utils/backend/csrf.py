__all__ = (
    "CsrfCookieToHeader",
)


# CSRF ERROR
class CsrfCookieToHeader:
    def process_request(self, request):
        csrftoken = request.COOKIES.get("csrftoken")
        if csrftoken:
            request.META["HTTP_X_CSRFTOKEN"] = csrftoken
