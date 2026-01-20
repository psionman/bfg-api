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
from common.utilities import get_user_from_username, GameRequest

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


def new_board(req: GameRequest) -> dict[str, object]:
    """Return the context after a new board has been generated."""
    return get_new_board(req)


def room_board(req: GameRequest) -> dict[str, object]:
    return get_room_board(req)


def board_from_pbn(req: dict):
    """Return board from a PBN string."""
    return get_board_from_pbn(req)


def get_history(req: dict):
    return get_history_boards_text(req)


def save_board_file(req: dict):
    return save_boards_file_to_room(req)


def get_archive_list(req: dict):
    return get_user_archive_list(req)


def get_board_file(req: dict):
    return get_board_file_from_room(req)


def history_board(req) -> Board:
    return get_history_board(req)


def rotate_boards(req: GameRequest) -> dict[str, object]:
    return rotate_archived_boards(req)


def bid_made(req: GameRequest) -> dict[str, str]:
    return get_bid_made(req)


def use_bid(req: GameRequest, use_suggested_bid=True) -> dict[str, str]:
    return get_bid_context(req, use_suggested_bid)


def cardplay_setup(req: GameRequest) -> dict[str, object]:
    """ Return the static context for cardplay."""
    return get_cardplay_context(req)


def card_played(req: GameRequest) -> dict[str, object]:
    """
        Add a card to the current trick and increment current player.
        if necessary, complete the trick.
    """
    return card_played_context(req)


def restart_board(req: GameRequest) -> dict[str, object]:
    """Return the context for restart board."""
    logger.info('restart-board', username=req.username)
    update_user_activity(req)
    return restart_board_context(req)


def replay_board(req: GameRequest) -> dict[str, object]:
    """Return the context for replay board."""
    logger.info('replay-board', username=req.username)
    update_user_activity(req)
    return replay_board_context(req)


def claim(req: dict):
    return claim_context(req)


def compare_scores(req: dict):
    return compare_scores_context(req)


def undo(req: dict):
    return undo_context(req)


def get_user_set_hands(req: dict):
    room = get_room_from_name(req.room_name)
    return {
        'set_hands': json.loads(room.set_hands),
        'use_set_hands': room.use_set_hands,
        'display_hand_type': room.display_hand_type,
    }


def set_user_set_hands(req: dict):
    room = get_room_from_name(req.room_name)
    print(f'{req.set_hands=}')
    room.set_hands = json.dumps(req.set_hands)
    room.use_set_hands = req.use_set_hands
    room.display_hand_type = req.display_hand_type
    room.save()
    update_user_activity(req)
    logger.info(
        'update-set-hands',
        username=req.username,
        set_hands=req.set_hands)


def package_versions():
    versions = {
        'api': api_version,
    }
    for package in PACKAGES:
        versions[package] = version(package)
    return versions


def message_sent(req: dict) -> None:
    logger.info(
        'message-sent',
        username=req.username,
        message=req.message)
    return None


def message_received(req: dict) -> None:
    logger.info(
        'message-received',
        username=req.username,
        message=req.message)
    return None


def database_update(req: dict) -> None:
    # logger.info(
    #     'database-update',
    #     username=req.username,
    #     payload=req.payload)
    update_user_activity(req)
    return None


def user_login(req: dict, ip_address: str) -> None:
    user = get_user_from_username(req.username)
    user.logged_in = True
    user.save()
    update_user_activity(req)
    logger.info(
        'login', username=req.username, ip_address=ip_address)
    return None


def user_logout(req: dict, ip_address: str) -> None:
    user = get_user_from_username(req.username)
    user.logged_in = False
    user.save()
    update_user_activity(req)
    logger.info('logout', username=req.username, ip_address=ip_address)
    return None


def get_user_status(req) -> dict:
    user = get_user_from_username(req.user_query)

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


def seat_assigned(req: dict) -> None:
    logger.info('seat-assigned', username=req.username, seat=req.seat)
    return None
