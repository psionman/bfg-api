import datetime
import logging
import json


logger = logging.getLogger('bfg')

DATE_FORMAT = '%Y-%b-%d %H:%M:%S'


def log(username, action, payload=None):
    """Create log message and return the message."""
    log_time = datetime.datetime.now().strftime(DATE_FORMAT)
    action_payload = f'<{action}>'
    if payload:
        action_payload = f'<{action}> {json.dumps(payload)}'

    log_text = f'{log_time} <{username}> {action_payload}'
    logger.debug(log_text)
    return log_text
