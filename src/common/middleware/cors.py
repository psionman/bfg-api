# common/middleware/cors.py
from django.conf import settings
from django.http import HttpResponse


class BfgCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")

        # Handle preflight OPTIONS for /bfg/ paths
        if request.method == "OPTIONS" and request.path.startswith("/bfg/"):
            response = HttpResponse(status=204)  # 204 No Content is preferred
        else:
            response = self.get_response(request)

        # Only add CORS headers for /bfg/ paths
        if not request.path.startswith("/bfg/"):
            return response

        # Dev override
        if getattr(settings, "BFG_CORS_ALLOW_ALL_DEV", False):
            response["Access-Control-Allow-Origin"] = origin or "*"
        # Production: exact match
        elif origin and origin in getattr(settings, "BFG_CORS_ALLOWED_ORIGINS", []):
            response["Access-Control-Allow-Origin"] = origin
        else:
            # No match – no CORS headers (correct behavior)
            return response

        # Standard headers
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        response["Access-Control-Allow-Headers"] = "X-CSRFToken, Content-Type, Authorization"
        response["Access-Control-Max-Age"] = "86400"

        return response
