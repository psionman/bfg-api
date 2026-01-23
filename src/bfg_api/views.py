import json

from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.models import Room
import common.application as app
from common.serializers import RoomSerializer
from common.utilities import req_from_json


def handle_request(params: str, func, *args) -> JsonResponse:
    req = req_from_json(params)
    return JsonResponse(func(req, *args), safe=False)


class StaticData(View):
    @staticmethod
    def get(request, params):
        context = app.static_data(request.META.get('REMOTE_ADDR'))
        print(type(context))
        return JsonResponse(context, safe=False)


class UserLogin(View):
    @staticmethod
    def post(request, params):
        return handle_request(
            params, app.user_login, request.META.get('REMOTE_ADDR'))

    @staticmethod
    def get(request, params):
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
        return handle_request(params, app.use_bid)

    @staticmethod
    def get(request, params):
        return UseSuggestedBid.post(request, params)


class UseOwnBid(View):
    @staticmethod
    def post(request, params):
        return handle_request(params, app.use_bid)

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
