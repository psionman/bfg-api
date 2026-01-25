
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from django.views.decorators.cache import never_cache

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.models import Room
import common.application as app
from common.serializers import RoomSerializer
from common.utilities import req_from_json


@ensure_csrf_cookie
@never_cache
def ensure_csrf(request):
    response = JsonResponse({"status": "csrftoken issued"})
    response["Cache-Control"] = "no-store"
    return response


def handle_request(request, func, *args) -> JsonResponse:
    req = req_from_json(request.body or {})
    return JsonResponse(func(req, *args), safe=False)


# def handle_get_request(params: str, func, *args) -> JsonResponse:
#     req = req_from_json(params)
#     return JsonResponse(func(req, *args), safe=False)


class StaticData(View):
    def post(self, request):
        return handle_request(
            request, app.static_data, request.META.get('REMOTE_ADDR'))


class UserLogin(View):
    def post(self, request):
        return handle_request(
            request, app.user_login, request.META.get('REMOTE_ADDR'))


class UserLogout(View):
    def post(self, request):
        return handle_request(
            request, app.user_logout, request.META.get('REMOTE_ADDR'))


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


# class GetArchiveList(View):
#     @staticmethod
#     def post(request):
#         """Return a list of boards."""
#         return handle_get_request(params, app.get_archive_list)


# class GetBoardFile(View):
#     @staticmethod
#     def post(request, params):
#         """Return board file."""
#         return handle_get_request(params, app.get_board_file)


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

# class GetParameters(View):
#     @staticmethod
#     def get(request, params):
#         req = req_from_json(params)
#         context = {
#             'slice': 200
#         }
#         return JsonResponse(context, safe=False)


# class SaveBoardFile(View):
#     @staticmethod
#     def get(request, params):
#         req = req_from_json(params)
#         context = {'boards_saved': False, }
#         if req.pbn_text:
#             context = app.save_board_file(req)
#         return JsonResponse(context, safe=False)


# class Versions(View):
#     @staticmethod
#     def post(request, params):
#         return handle_get_request(params, app.package_versions)

#     @staticmethod
#     def get(request, params):
#         return Versions.post(request, params)


class MessageSent(View):
    def post(self, request):
        return handle_request(request, app.message_sent)


class MessageReceived(View):
    def post(self, request):
        return handle_request(request, app.message_received)


class DatabaseUpdate(View):
    def post(self, request):
        return handle_request(request, app.database_update)


# class UserStatus(View):
#     def post(self, request):
#         return handle_request(request, app.get_user_status)


# class RoomListApiView(APIView):
#     # add permission to check if user is authenticated
#     # permission_classes = [permissions.IsAuthenticated]

#     # 1. list all
#     def get(self, request, *args, **kwargs):
#         '''
#         list all the Room items for given requested user
#         '''
#         rooms = Room.objects.all()
#         serializer = RoomSerializer(rooms, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     # 2. Create
#     def post(self, request, *args, **kwargs):
#         '''
#         Create the Room with given Room data
#         '''
#         data = {
#             'name': request.data.get('room_name'),
#             'mode': request.data.get('mode'),
#             'last_task': request.data.get('last_task'),
#             'last_data': request.data.get('last_data'),
#             'board': request.data.get('board'),
#         }
#         serializer = RoomSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RoomDetailApiView(APIView):
#     # add permission to check if user is authenticated
#     # permission_classes = [permissions.IsAuthenticated]

#     def get_object(self, room_name):
#         '''
#         Helper method to get the object with given room_name, and user_id
#         '''
#         try:
#             return Room.objects.get(name=room_name)
#         except Room.DoesNotExist:
#             return None

#     # 3. Retrieve
#     def get(self, request, room_name, *args, **kwargs):
#         '''
#         Retrieves the Room with given room_name
#         '''
#         room_instance = self.get_object(room_name)
#         if not room_instance:
#             return Response(
#                 {"res": "Object with Room id does not exists"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = RoomSerializer(room_instance)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     # 4. Update
#     def put(self, request, room_name, *args, **kwargs):
#         '''
#         Updates the Room item with given room_name if exists
#         '''
#         room_instance = self.get_object(room_name)
#         if not room_instance:
#             return Response(
#                 {"res": "Object with Room id does not exists"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         data = {
#             'name': request.data.get('room_name'),
#             'mode': request.data.get('mode'),
#             'last_task': request.data.get('last_task'),
#             'last_data': request.data.get('last_data'),
#             'board': request.data.get('board'),
#         }
#         serializer = RoomSerializer(instance=room_instance, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     # 5. Delete
#     def delete(self, request, room_name, *args, **kwargs):
#         '''
#         Deletes the Room item with given room_name if exists
#         '''
#         room_instance = self.get_object(room_name)
#         if not room_instance:
#             return Response(
#                 {"res": "Object with Room id does not exists"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         room_instance.delete()
#         return Response(
#             {"res": "Object deleted!"},
#             status=status.HTTP_200_OK
#         )
