"""API functionality for BfG."""

from importlib.metadata import version
from datetime import timedelta
import json
import structlog
from django.utils import timezone

from bridgeobjects import CALLS
from bfgdealer import Board, SOLO_SET_HANDS, DUO_SET_HANDS

from common.constants import PACKAGES
from common.utilities import get_room_from_name, update_user_activity
from common.images import CURSOR, CALL_IMAGES, CARD_IMAGES
from common.archive import (
    get_history_boards_text, rotate_archived_boards, save_boards_file_to_room,
    get_user_archive_list, get_board_file_from_room)
from common.board import (
    get_new_board, get_history_board, get_board_from_pbn, undo_context,
    get_room_board, restart_board_context)

from common.bidding import get_bid_made, get_bid_context
from common.cardplay import (
    get_cardplay_context, card_played_context, replay_board_context,
    claim_context, compare_scores_context)
from common.constants import SOURCES
from common.utilities import get_user_from_username

from _version import __version__ as api_version

logger = structlog.get_logger()


def static_data(ip_address: str) -> dict[str, object]:
    """Return a dict of static data."""
    logger.info('Static data', ip_address=ip_address)
    context = {
        'card_images': CARD_IMAGES,
        'call_images': CALL_IMAGES,
        'cursor': CURSOR,
        'calls': CALLS,
        'solo_set_hands': SOLO_SET_HANDS,
        'duo_set_hands': DUO_SET_HANDS,
        'sources': SOURCES,
        'versions': package_versions(),
    }
    context['call_images']['A'] = context['call_images']['alert']
    return context


def new_board(params: dict[str, str]) -> dict[str, object]:
    """Return the context after a new board has been generated."""
    return get_new_board(params)


def room_board(params: dict[str, str]) -> dict[str, object]:
    return get_room_board(params)


def board_from_pbn(params: dict):
    """Return board from a PBN string."""
    return get_board_from_pbn(params)


def get_history(params: dict):
    return get_history_boards_text(params)


def save_board_file(params: dict):
    return save_boards_file_to_room(params)


def get_archive_list(params: dict):
    return get_user_archive_list(params)


def get_board_file(params: dict):
    return get_board_file_from_room(params)


def history_board(params) -> Board:
    return get_history_board(params)


def rotate_boards(params: dict[str, str]) -> dict[str, object]:
    return rotate_archived_boards(params)


def bid_made(params: dict[str, str]) -> dict[str, str]:
    return get_bid_made(params)


def use_bid(params: dict[str, str], use_suggested_bid=True) -> dict[str, str]:
    return get_bid_context(params, use_suggested_bid)


def cardplay_setup(params: dict[str, str]) -> dict[str, object]:
    """ Return the static context for cardplay."""
    return get_cardplay_context(params)


def card_played(params: dict[str, str]) -> dict[str, object]:
    """
        Add a card to the current trick and increment current player.
        if necessary, complete the trick.
    """
    return card_played_context(params)


def restart_board(params: dict[str, str]) -> dict[str, object]:
    """Return the context for restart board."""
    logger.info('restart-board', username=params.username)
    update_user_activity(params)
    return restart_board_context(params)


def replay_board(params: dict[str, str]) -> dict[str, object]:
    """Return the context for replay board."""
    logger.info('replay-board', username=params.username)
    update_user_activity(params)
    return replay_board_context(params)


def claim(params: dict):
    return claim_context(params)


def compare_scores(params: dict):
    return compare_scores_context(params)


def undo(params: dict):
    return undo_context(params)


def get_user_set_hands(params: dict):
    room = get_room_from_name(params.room_name)
    return {
        'set_hands': json.loads(room.set_hands),
        'use_set_hands': room.use_set_hands,
        'display_hand_type': room.display_hand_type,
    }


def set_user_set_hands(params: dict):
    room = get_room_from_name(params.room_name)
    print(f'{params.set_hands=}')
    room.set_hands = json.dumps(params.set_hands)
    room.use_set_hands = params.use_set_hands
    room.display_hand_type = params.display_hand_type
    room.save()
    update_user_activity(params)
    logger.info(
        'update-set-hands',
        username=params.username,
        set_hands=params.set_hands)


def package_versions():
    versions = {
        'api': api_version,
    }
    for package in PACKAGES:
        versions[package] = version(package)
    return versions


def message_sent(params: dict) -> None:
    logger.info(
        'message-sent',
        username=params.username,
        message=params.message)
    return None


def message_received(params: dict) -> None:
    logger.info(
        'message-received',
        username=params.username,
        message=params.message)
    return None


def database_update(params: dict) -> None:
    # logger.info(
    #     'database-update',
    #     username=params.username,
    #     payload=params.payload)
    update_user_activity(params)
    return None


def user_login(params: dict, ip_address: str) -> None:
    user = get_user_from_username(params.username)
    user.logged_in = True
    user.save()
    update_user_activity(params)
    logger.info(
        'login', username=params.username, ip_address=ip_address)
    return None


def user_logout(params: dict, ip_address: str) -> None:
    user = get_user_from_username(params.username)
    user.logged_in = False
    user.save()
    update_user_activity(params)
    logger.info('logout', username=params.username, ip_address=ip_address)
    return None


def get_user_status(params) -> dict:
    user = get_user_from_username(params.user_query)

    last_activity_iso = None
    if user.last_activity:
        time_diff = abs(timezone.now() - user.last_activity)
        if time_diff > timedelta(hours=1):
            user.logged_in = False
            user.save()

        last_activity_iso = (
            user.last_activity
            .replace(microsecond=(user.last_activity.microsecond // 1000) * 1000)  # milliseconds only
            .isoformat()
            .replace('+00:00', 'Z')  # if it's UTC-aware
        )

    return {
        'logged_in': user.logged_in,
        'last_activity': last_activity_iso,
    }


def seat_assigned(params: dict) -> None:
    logger.info('seat-assigned', username=params.username, seat=params.seat)
    return None
