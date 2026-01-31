
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from django.views.decorators.cache import never_cache

import common.application as app
from common.utilities import req_from_json


@ensure_csrf_cookie
@never_cache
def ensure_csrf(request):
    response = JsonResponse({"status": "csrftoken issued"})
    response["Cache-Control"] = "no-store"
    return response


def handle_request(request, func, *args) -> JsonResponse:
    raw = request.body or b'{}'
    req = req_from_json(raw)
    return JsonResponse(func(req, *args), safe=False)


class StaticData(View):
    def get(self, request):
        return JsonResponse(
            app.static_data(request.META.get('REMOTE_ADDR')),
            safe=False
        )


class UserLogin(View):
    def post(self, request):
        return handle_request(
            request, app.user_login, request.META.get('REMOTE_ADDR'))


class UserLogout(View):
    def post(self, request):
        return handle_request(
            request, app.user_logout, request.META.get('REMOTE_ADDR'))


class UserStatus(View):
    def get(self, request):
        raw = request.body or b'{}'
        req = req_from_json(raw)
        return JsonResponse(app.get_user_status(req),safe=False)


class UserSeat(View):
    def post(self, request):
        return handle_request(request, app.seat_assigned)


class GetUserSetHands(View):
    def post(self, request):
        return handle_request(request, app.get_user_set_hands)


class SetUserSetHands(View):
    def post(self, request):
        return handle_request(request, app.set_user_set_hands)


class NewBoard(View):
    def post(self, request):
        return handle_request(request, app.new_board)


class RoomBoard(View):
    def post(self, request):
        return handle_request(request, app.room_board)


class PbnBoard(View):
    def post(self, request):
        """Return board from a PBN string."""
        return handle_request(request, app.board_from_pbn)


class GetHistory(View):
    def post(self, request):
        """Return board archive."""
        return handle_request(request, app.get_history)


class BidMade(View):
    def post(self, request):
        return handle_request(request, app.bid_made)


class UseSuggestedBid(View):
    def post(self, request):
        return handle_request(request, app.use_bid, True)


class UseOwnBid(View):
    def post(self, request):
        return handle_request(request, app.use_bid, False)


class CardPlay(View):
    def post(self, request):
        return handle_request(request, app.cardplay_setup)


class CardPlayed(View):
    def post(self, request):
        return handle_request(request, app.card_played)


class RestartBoard(View):
    def post(self, request):
        return handle_request(request, app.restart_board)


class ReplayBoard(View):
    def post(self, request):
        return handle_request(request, app.replay_board)


class UseHistoryBoard(View):
    def post(self, request):
        return handle_request(request, app.history_board)


class RotateBoards(View):
    def post(self, request):
        return handle_request(request, app.rotate_boards)


class Claim(View):
    def post(self, request):
        return handle_request(request, app.claim)


class CompareScores(View):
    def post(self, request):
        return handle_request(request, app.compare_scores)


class Undo(View):
    def post(self, request):
        return handle_request(request, app.undo)


class MessageSent(View):
    def post(self, request):
        return handle_request(request, app.message_sent)


class MessageReceived(View):
    def post(self, request):
        return handle_request(request, app.message_received)


class DatabaseUpdate(View):
    def post(self, request):
        return handle_request(request, app.database_update)
