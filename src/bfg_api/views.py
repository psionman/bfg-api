
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import structlog

import common.application as app
from common.utilities import req_from_json

logger = structlog.get_logger()


@ensure_csrf_cookie
@never_cache
def ensure_csrf(request):
    token = get_token(request)  # force generation
    logger.info('cookie', csrf_token=token)
    return JsonResponse({
        'status': 'ok',
        'csrftoken': token  # send it in body too – easier for JS
    })


def handle_request(request, func, *args) -> JsonResponse:
    raw = request.body or b'{}'
    req = req_from_json(raw)
    return JsonResponse(func(req, *args), safe=False)


class debug_view(View):
    def get(self, request):
        output = f"""
            <h1>Request Debug Info</h1>
            <p><strong>Host header:</strong> {request.get_host()}</p>
            <p><strong>Full META:</strong></p>
            <pre>{request.META}</pre>
            <p><strong>Is secure (HTTPS):</strong> {request.is_secure()}</p>
            <p><strong>Scheme:</strong> {request.scheme}</p>
        """
        return HttpResponse(output)


@method_decorator(csrf_exempt, name="dispatch")
class StaticData(View):
    def get(self, request):
        # logger.info(
        #     'static-data',
        #     versions=app.static_data(
        #         request.META.get('REMOTE_ADDR')
        #         )['versions'])
        return JsonResponse(
            app.static_data(request.META.get('REMOTE_ADDR')),
            safe=False
        )


@method_decorator(csrf_exempt, name="dispatch")
class UserLogin(View):
    def post(self, request):
        return handle_request(
            request, app.user_login, request.META.get('REMOTE_ADDR'))


@method_decorator(csrf_exempt, name="dispatch")
class UserLogout(View):
    def post(self, request):
        return handle_request(
            request, app.user_logout, request.META.get('REMOTE_ADDR'))


@method_decorator(csrf_exempt, name="dispatch")
class UserStatus(View):
    def get(self, request):
        raw = request.body or b'{}'
        req = req_from_json(raw)
        return JsonResponse(app.get_user_status(req),safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class UserSeat(View):
    def post(self, request):
        return handle_request(request, app.seat_assigned)


@method_decorator(csrf_exempt, name="dispatch")
class GetUserSetHands(View):
    def post(self, request):
        return handle_request(request, app.get_user_set_hands)


@method_decorator(csrf_exempt, name="dispatch")
class SetUserSetHands(View):
    def post(self, request):
        return handle_request(request, app.set_user_set_hands)


@method_decorator(csrf_exempt, name="dispatch")
class NewBoard(View):
    def post(self, request):
        return handle_request(request, app.new_board)


@method_decorator(csrf_exempt, name="dispatch")
class RoomBoard(View):
    def post(self, request):
        return handle_request(request, app.room_board)


@method_decorator(csrf_exempt, name="dispatch")
class PbnBoard(View):
    def post(self, request):
        """Return board from a PBN string."""
        return handle_request(request, app.board_from_pbn)


@method_decorator(csrf_exempt, name="dispatch")
class GetHistory(View):
    def post(self, request):
        """Return board archive."""
        return handle_request(request, app.get_history)


@method_decorator(csrf_exempt, name="dispatch")
class BidMade(View):
    def post(self, request):
        return handle_request(request, app.bid_made)


@method_decorator(csrf_exempt, name="dispatch")
class UseSuggestedBid(View):
    def post(self, request):
        return handle_request(request, app.use_bid, True)


@method_decorator(csrf_exempt, name="dispatch")
class UseOwnBid(View):
    def post(self, request):
        return handle_request(request, app.use_bid, False)


@method_decorator(csrf_exempt, name="dispatch")
class CardPlay(View):
    def post(self, request):
        return handle_request(request, app.cardplay_setup)


@method_decorator(csrf_exempt, name="dispatch")
class CardPlayed(View):
    def post(self, request):
        return handle_request(request, app.card_played)


@method_decorator(csrf_exempt, name="dispatch")
class RestartBoard(View):
    def post(self, request):
        return handle_request(request, app.restart_board)


@method_decorator(csrf_exempt, name="dispatch")
class ReplayBoard(View):
    def post(self, request):
        return handle_request(request, app.replay_board)


@method_decorator(csrf_exempt, name="dispatch")
class UseHistoryBoard(View):
    def post(self, request):
        return handle_request(request, app.history_board)


@method_decorator(csrf_exempt, name="dispatch")
class RotateBoards(View):
    def post(self, request):
        return handle_request(request, app.rotate_boards)


@method_decorator(csrf_exempt, name="dispatch")
class Claim(View):
    def post(self, request):
        return handle_request(request, app.claim)


@method_decorator(csrf_exempt, name="dispatch")
class CompareScores(View):
    def post(self, request):
        return handle_request(request, app.compare_scores)


@method_decorator(csrf_exempt, name="dispatch")
class Undo(View):
    def post(self, request):
        return handle_request(request, app.undo)


@method_decorator(csrf_exempt, name="dispatch")
class MessageSent(View):
    def post(self, request):
        return handle_request(request, app.message_sent)


@method_decorator(csrf_exempt, name="dispatch")
class MessageReceived(View):
    def post(self, request):
        return handle_request(request, app.message_received)


@method_decorator(csrf_exempt, name="dispatch")
class DatabaseUpdate(View):
    def post(self, request):
        return handle_request(request, app.database_update)
