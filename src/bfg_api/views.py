import json

from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponse, JsonResponse
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
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
    # response = JsonResponse({"status": "csrf cookie set"})
    # response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    # response["Pragma"] = "no-cache"
    # return response
    # return JsonResponse({"status": "csrftoken set"})
    response = JsonResponse({"status": "csrftoken issued"})
    response["Cache-Control"] = "no-store"
    return response


def handle_post_request(request, func, *args) -> JsonResponse:
    req = req_from_json(request.body)
    return JsonResponse(func(req, *args), safe=False)


def handle_request(params: str, func, *args) -> JsonResponse:
    req = req_from_json(params)
    return JsonResponse(func(req, *args), safe=False)


class StaticData(View):
    def get(self, request, params):
        context = app.static_data(request.META.get('REMOTE_ADDR'))
        return JsonResponse(context, safe=False)


class UserLogin(View):
    def post(self, request):
        return handle_request(
            request.body,
            app.user_login, request.META.get('REMOTE_ADDR'))

    def get(self, request, params):
        return UserLogin.post(request, params)


class UserLogout(View):
    @staticmethod
    def post(request, params):
        return handle_request(
            params, app.user_logout, request.META.get('REMOTE_ADDR'))

    @staticmethod
    def get(request, params):
        return UserLogout.post(request, params)


class UserSeat(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.seat_assigned)

    @staticmethod
    def get(request, params):
        return UserSeat.post(request, params)


class GetUserSetHands(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.get_user_set_hands)

    @staticmethod
    def get(request, params):
        return GetUserSetHands.post(request, params)


class SetUserSetHands(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.set_user_set_hands)

    @staticmethod
    def get(request, params):
        return SetUserSetHands.post(request, params)



class NewBoard(View):
    @staticmethod
    def post(request, params):
        req = req_from_json(params)
        return handle_request(params, app.new_board)

    @staticmethod
    def get(request, params):
        return NewBoard.post(request, params)


class RoomBoard(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.room_board)

    @staticmethod
    def get(request, params):
        return RoomBoard.post(request, params)


class PbnBoard(View):
    @staticmethod
    def post(request, params):
        """Return board from a PBN string."""
        return handle_request(params, app.board_from_pbn)

    @staticmethod
    def get(request, params):
        return PbnBoard.post(request, params)


class GetHistory(View):
    @staticmethod
    def post(request, params):
        """Return board archive."""
        return handle_request(params, app.get_history)

    @staticmethod
    def get(request, params):
        return GetHistory.post(request, params)


class GetArchiveList(View):
    @staticmethod
    def post(request, params):
        """Return a file of boards."""
        return handle_request(params, app.get_archive_list)

    @staticmethod
    def get(request, params):
        return GetArchiveList.post(request, params)


class GetBoardFile(View):
    @staticmethod
    def post(request, params):
        """Return board file."""
        return handle_request(params, app.get_board_file)

    @staticmethod
    def get(request, params):
        return GetBoardFile.post(request, params)


class BidMade(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.bid_made)

    @staticmethod
    def get(request, params):
        return BidMade.post(request, params)


class UseSuggestedBid(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.use_bid, True)

    @staticmethod
    def get(request, params):
        return UseSuggestedBid.post(request, params)


class UseOwnBid(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.use_bid, False)

    @staticmethod
    def get(request, params):
        return UseOwnBid.post(request, params)


class CardPlay(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.cardplay_setup)

    @staticmethod
    def get(request, params):
        return CardPlay.post(request, params)


class CardPlayed(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.card_played)

    @staticmethod
    def get(request, params):
        return CardPlayed.post(request, params)


class RestartBoard(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.restart_board)

    @staticmethod
    def get(request, params):
        return RestartBoard.post(request, params)


class ReplayBoard(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.replay_board)

    @staticmethod
    def get(request, params):
        return ReplayBoard.post(request, params)


class UseHistoryBoard(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.history_board)

    @staticmethod
    def get(request, params):
        return UseHistoryBoard.post(request, params)


class RotateBoards(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.rotate_boards)

    @staticmethod
    def get(request, params):
        return RotateBoards.post(request, params)



class Claim(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.claim)

    @staticmethod
    def get(request, params):
        return Claim.post(request, params)


class CompareScores(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.compare_scores)

    @staticmethod
    def get(request, params):
        return CompareScores.post(request, params)


class Undo(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.undo)

    @staticmethod
    def get(request, params):
        return Undo.post(request, params)


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


class Versions(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.package_versions)

    @staticmethod
    def get(request, params):
        return Versions.post(request, params)


class MessageSent(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.message_sent)

    @staticmethod
    def get(request, params):
        return MessageSent.post(request, params)


class MessageReceived(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.message_received)

    @staticmethod
    def get(request, params):
        return MessageReceived.post(request, params)


class DatabaseUpdate(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.database_update)

    @staticmethod
    def get(request, params):
        return DatabaseUpdate.post(request, params)


class UserStatus(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.get_user_status)

    @staticmethod
    def get(request, params):
        return UserStatus.post(request, params)



class RoomListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. list all
    def get(self, request, *args, **kwargs):
        '''
        list all the Room items for given requested user
        '''
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. Create
    def post(self, request, *args, **kwargs):
        '''
        Create the Room with given Room data
        '''
        data = {
            'name': request.data.get('room_name'),
            'mode': request.data.get('mode'),
            'last_task': request.data.get('last_task'),
            'last_data': request.data.get('last_data'),
            'board': request.data.get('board'),
        }
        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetailApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self, room_name):
        '''
        Helper method to get the object with given room_name, and user_id
        '''
        try:
            return Room.objects.get(name=room_name)
        except Room.DoesNotExist:
            return None

    # 3. Retrieve
    def get(self, request, room_name, *args, **kwargs):
        '''
        Retrieves the Room with given room_name
        '''
        room_instance = self.get_object(room_name)
        if not room_instance:
            return Response(
                {"res": "Object with Room id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RoomSerializer(room_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 4. Update
    def put(self, request, room_name, *args, **kwargs):
        '''
        Updates the Room item with given room_name if exists
        '''
        room_instance = self.get_object(room_name)
        if not room_instance:
            return Response(
                {"res": "Object with Room id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'name': request.data.get('room_name'),
            'mode': request.data.get('mode'),
            'last_task': request.data.get('last_task'),
            'last_data': request.data.get('last_data'),
            'board': request.data.get('board'),
        }
        serializer = RoomSerializer(instance=room_instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 5. Delete
    def delete(self, request, room_name, *args, **kwargs):
        '''
        Deletes the Room item with given room_name if exists
        '''
        room_instance = self.get_object(room_name)
        if not room_instance:
            return Response(
                {"res": "Object with Room id does not exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        room_instance.delete()
        return Response(
            {"res": "Object deleted!"},
            status=status.HTTP_200_OK
        )
