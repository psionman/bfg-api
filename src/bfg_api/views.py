import json

from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.models import Room
import common.application as app
from common.serializers import RoomSerializer
from common.utilities import req_from_json, GameRequest


def handle_request(params: dict, func):
    req = req_from_json(params)
    return JsonResponse(func(req), safe=False)


class StaticData(View):
    @staticmethod
    def get(request, params):
        context = app.static_data(request.META.get('REMOTE_ADDR'))
        return JsonResponse(context, safe=False)


class UserLogin(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        app.user_login(req, request.META.get('REMOTE_ADDR'))

        return JsonResponse({}, safe=False)


class UserLogout(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        app.user_logout(req, request.META.get('REMOTE_ADDR'))
        return JsonResponse({}, safe=False)


class UserSeat(View):
    @staticmethod
    def get(request, params):
        return handle_request(params, app.seat_assigned)


class GetUserSetHands(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.get_user_set_hands(req)
        return JsonResponse(context, safe=False)


class SetUserSetHands(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.set_user_set_hands(req)
        return JsonResponse(context, safe=False)


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


class NewBoard(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.new_board(req)
        if req.browser:
            return JsonResponse(json.dumps(context), safe=False)
        return JsonResponse(context, safe=False)


class RoomBoard(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.room_board(req)
        return JsonResponse(context, safe=False)


class PbnBoard(View):
    @staticmethod
    def get(request, params):
        """Return board from a PBN string."""
        req = req_from_json(params)
        context = app.board_from_pbn(req)
        return JsonResponse(context, safe=False)


class GetHistory(View):
    @staticmethod
    def get(request, params):
        """Return board archive."""
        req = req_from_json(params)
        context = app.get_history(req)
        return JsonResponse(context, safe=False)


class GetArchiveList(View):
    @staticmethod
    def get(request, params):
        """Return a file of boards."""
        req = req_from_json(params)
        context = app.get_archive_list(req)
        return JsonResponse(context, safe=False)


class GetBoardFile(View):
    @staticmethod
    def get(request, params):
        """Return board file."""
        req = req_from_json(params)
        context = app.get_board_file(req)
        return JsonResponse(context, safe=False)


class BidMade(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.bid_made(req)
        return JsonResponse(context, safe=False)


class UseSuggestedBid(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.use_bid(req, use_suggested_bid=True)
        return JsonResponse(context, safe=False)


class UseOwnBid(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.use_bid(req, use_suggested_bid=False)
        return JsonResponse(context, safe=False)


class CardPlay(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.cardplay_setup(req)
        return JsonResponse(context, safe=False)


class CardPlayed(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.card_played(req)
        return JsonResponse(context, safe=False)


class RestartBoard(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.restart_board(req)
        return JsonResponse(context, safe=False)


class ReplayBoard(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.replay_board(req)
        return JsonResponse(context, safe=False)


class UseHistoryBoard(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.history_board(req)
        return JsonResponse(context, safe=False)


class RotateBoards(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.rotate_boards(req)
        return JsonResponse(context, safe=False)


class Claim(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.claim(req)
        return JsonResponse(context, safe=False)


class CompareScores(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.compare_scores(req)
        return JsonResponse(context, safe=False)


class Undo(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.undo(req)
        return JsonResponse(context, safe=False)


class GetParameters(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = {
            'slice': 200
        }
        return JsonResponse(context, safe=False)


class SaveBoardFile(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = {'boards_saved': False, }
        if req.pbn_text:
            context = app.save_board_file(req)
        return JsonResponse(context, safe=False)


class Versions(View):
    @staticmethod
    def get(request):
        context = app.package_versions()
        return JsonResponse(context, safe=False)


class MessageSent(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.message_sent(req)
        return JsonResponse(context, safe=False)


class MessageReceived(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.message_received(req)
        return JsonResponse(context, safe=False)


class DatabaseUpdate(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.database_update(req)
        return JsonResponse(context, safe=False)


class UserStatus(View):
    @staticmethod
    def get(request, params):
        req = req_from_json(params)
        context = app.get_user_status(req)
        return JsonResponse(context, safe=False)
