"""
To test live server:

https://bidforgame.com/bfg/versions/

"""

from django.urls import path
from . import views


urlpatterns = [
    # Static data
    path('ensure-csrf/', views.ensure_csrf),
    path('static-data/', views.StaticData.as_view()),

    # user login/out
    path('user-login/', views.UserLogin.as_view()),
    path('user-seat/', views.UserSeat.as_view()),
    path('user-logout/', views.UserLogout.as_view()),
    # path('user-status/', views.UserStatus.as_view()),

    # REST api
    # path('api', views.RoomListApiView.as_view()),
    # path('api/<str:room_name>', views.RoomDetailApiView.as_view()),

    # Room
    path('get-user-set-hands/', views.GetUserSetHands.as_view()),
    path('set-user-set-hands/', views.SetUserSetHands.as_view()),

    # Boards
    path('new-board/', views.NewBoard.as_view()),
    path('restart-board/', views.RestartBoard.as_view()),
    path('replay-board/', views.ReplayBoard.as_view()),
    path('room-board/', views.RoomBoard.as_view()),
    path('pbn-board/', views.PbnBoard.as_view()),

    # History
    path('use-history-board/', views.UseHistoryBoard.as_view()),
    path('get-history/', views.GetHistory.as_view()),
    path('rotate-boards/', views.RotateBoards.as_view()),

    # path('save-board-file/<str:params>/', views.SaveBoardFilePut.as_view()),
    # path('get-archive-list/<str:params>/', views.GetArchiveList.as_view()),
    # path('get-board-file/<str:params>/', views.GetBoardFile.as_view()),
    # path('save-board-file/<str:params>/', views.SaveBoardFile.as_view()),

    # Bids
    path('bid-made/', views.BidMade.as_view()),
    path('use-suggestion/', views.UseSuggestedBid.as_view()),
    path('use-own-bid/', views.UseOwnBid.as_view()),

    # Card play
    path('cardplay/', views.CardPlay.as_view()),
    path('card-played/', views.CardPlayed.as_view()),
    path('claim/', views.Claim.as_view()),
    path('compare-scores/', views.CompareScores.as_view()),

    # Utilities
    path('undo/', views.Undo.as_view()),
    # path('versions/', views.Versions.as_view()),
    # path('get-parameters/<str:params>/', views.GetParameters.as_view()),
    path('database-update/', views.DatabaseUpdate.as_view()),


    # Messages
    path('message-sent/', views.MessageSent.as_view()),
    path('message-received/', views.MessageReceived.as_view()),
]
