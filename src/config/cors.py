# config/cors.py


def bfg_cors_allowed_origins(return_list=True):
    if return_list:
        return [
            "https://bidforgame.netlify.app",
        ]
    else:
        return ("https://bidforgame.netlify.app",)


def cors_allowed_origins(debug: bool = False, dev_ports=None):
    allowed_origins = [
        "https://www.bidforgame.com",
        "https://bidforgame.com",
        "https://bidforgame.co.uk",
        "https://www.bidforgame.co.uk",
        "https://bidforgame.netlify.app",
    ]

    # dev convenience
    if debug and dev_ports:
        for port in dev_ports:
            allowed_origins.extend(
                [
                    f"http://localhost:{port}",
                    f"http://127.0.0.1:{port}",
                ]
            )
            # CSRF_TRUSTED_ORIGINS.extend(
            #     [
            #         f"http://localhost:{port}",
            #         f"http://127.0.0.1:{port}",
            #     ]
            # )
    return allowed_origins


def cors_allowed_origin_regexes():
    return [
        r"^https://.*\.netlify\.app$",
    ]


# Explicitly allow OPTIONS
def cors_allow_methods():
    return [
        "DELETE",
        "GET",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]


def cors_allow_headers():
    return [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
    ]
