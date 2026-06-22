# config/csrf.py


def csrf_trusted_origins(debug: bool = False, dev_ports=None):
    trusted_origins = [
        # Production ones – include scheme!
        "https://www.bidforgame.com",
        "https://bidforgame.com",
        "https://bidforgame.co.uk",
        "https://bidforgame.netlify.app",
        "https://*.netlify.app",
        # If you have subdomains or variants later: 'https://*.bidforgame.com'
    ]
    # dev convenience
    if debug and dev_ports:
        for port in dev_ports:
            trusted_origins.extend(
                [
                    f"http://localhost:{port}",
                    f"http://127.0.0.1:{port}",
                ]
            )
    return trusted_origins


def csrf_cookie_samesite(debug: bool):
    if debug:
        return "Lax"
    else:
        return "None"  # Not sure about this in production


def csrf_cookie_secure(debug: bool):
    if debug:
        return False
    else:
        return True


def session_cookie_secure(debug: bool):
    return csrf_cookie_secure(debug)
