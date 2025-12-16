import json
import structlog

from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from common.models import Room
import common.application as app
from common.serializers import RoomSerializer
from common.utilities import Params

logger = structlog.get_logger()


class UserLogin(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        ip_address = request.META.get('REMOTE_ADDR')
        logger.info(
            'User logged in', username=params.username, ip_address=ip_address)
        return JsonResponse({}, safe=False)


class UserLogout(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        ip_address = request.META.get('REMOTE_ADDR')
        logger.info(
            'User logged out', username=params.username, ip_address=ip_address)
        return JsonResponse({}, safe=False)


class UserSeat(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        logger.info(
            'User seat allocate.', username=params.username, seat=params.seat)
        return JsonResponse({}, safe=False)


class StaticData(View):
    @staticmethod
    def get(request, params):
        ip_address = request.META.get('REMOTE_ADDR')
        logger.info(
            'Access static data', ip_address=ip_address)
        params = Params(params)
        context = app.static_data()
        return JsonResponse(context, safe=False)


class GetUserSetHands(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.get_user_set_hands(params)
        return JsonResponse(context, safe=False)


class SetUserSetHands(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.set_user_set_hands(params)
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
        params = Params(params)
        context = app.new_board(params)
        if params.browser:
            return JsonResponse(json.dumps(context), safe=False)
        return JsonResponse(context, safe=False)


class RoomBoard(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.room_board(params)
        return JsonResponse(context, safe=False)


class PbnBoard(View):
    @staticmethod
    def get(request, params):
        """Return board from a PBN string."""
        params = Params(params)
        context = app.board_from_pbn(params)
        return JsonResponse(context, safe=False)


class GetHistory(View):
    @staticmethod
    def get(request, params):
        """Return board archive."""
        params = Params(params)
        context = app.get_history(params)
        return JsonResponse(context, safe=False)


class GetArchiveList(View):
    @staticmethod
    def get(request, params):
        """Return a file of boards."""
        params = Params(params)
        context = app.get_archive_list(params)
        return JsonResponse(context, safe=False)


class GetBoardFile(View):
    @staticmethod
    def get(request, params):
        """Return board file."""
        params = Params(params)
        context = app.get_board_file(params)
        return JsonResponse(context, safe=False)


class BidMade(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.bid_made(params)
        return JsonResponse(context, safe=False)


class UseSuggestedBid(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.use_bid(params, use_suggested_bid=True)
        return JsonResponse(context, safe=False)


class UseOwnBid(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.use_bid(params, use_suggested_bid=False)
        return JsonResponse(context, safe=False)


class CardPlay(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.cardplay_setup(params)
        return JsonResponse(context, safe=False)


class CardPlayed(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.card_played(params)
        return JsonResponse(context, safe=False)


class RestartBoard(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.restart_board(params)
        return JsonResponse(context, safe=False)


class ReplayBoard(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.replay_board(params)
        return JsonResponse(context, safe=False)


class UseHistoryBoard(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.history_board(params)
        return JsonResponse(context, safe=False)


class RotateBoards(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.rotate_boards(params)
        return JsonResponse(context, safe=False)


class Claim(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.claim(params)
        return JsonResponse(context, safe=False)


class CompareScores(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.compare_scores(params)
        return JsonResponse(context, safe=False)


class Undo(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = app.undo(params)
        return JsonResponse(context, safe=False)


class GetParameters(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = {
            'slice': 200
        }
        return JsonResponse(context, safe=False)


class SaveBoardFile(View):
    @staticmethod
    def get(request, params):
        params = Params(params)
        context = {'boards_saved': False, }
        if params.pbn_text:
            context = app.save_board_file(params)
        return JsonResponse(context, safe=False)


class Versions(View):
    @staticmethod
    def get(request):
        context = app.package_versions()
        return JsonResponse(context, safe=False)
