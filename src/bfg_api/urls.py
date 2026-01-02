"""
To test live server:

https://bidforgame.com/bfg/versions/

"""


# from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    # Static data
    path('static-data/<str:params>/', views.StaticData.as_view()),

    # user login/out
    path('user-login/<str:params>/', views.UserLogin.as_view()),
    path('user-seat/<str:params>/', views.UserSeat.as_view()),
    path('user-logout/<str:params>/', views.UserLogout.as_view()),
    path('user-status/<str:params>/', views.UserStatus.as_view()),

    # REST api
    path('api', views.RoomListApiView.as_view()),
    path('api/<str:room_name>', views.RoomDetailApiView.as_view()),

    # Room
    path('get-user-set-hands/<str:params>/', views.GetUserSetHands.as_view()),
    path('set-user-set-hands/<str:params>/', views.SetUserSetHands.as_view()),

    # Boards
    path('new-board/<str:params>/', views.NewBoard.as_view()),
    path('restart-board/<str:params>/', views.RestartBoard.as_view()),
    path('replay-board/<str:params>/', views.ReplayBoard.as_view()),
    path('room-board/<str:params>/', views.RoomBoard.as_view()),
    path('pbn-board/<str:params>/', views.PbnBoard.as_view()),

    # History
    path('use-history-board/<str:params>/', views.UseHistoryBoard.as_view()),
    path('get-history/<str:params>/', views.GetHistory.as_view()),
    path('rotate-boards/<str:params>/', views.RotateBoards.as_view()),

    # path('save-board-file/<str:params>/', views.SaveBoardFilePut.as_view()),
    path('get-archive-list/<str:params>/', views.GetArchiveList.as_view()),
    path('get-board-file/<str:params>/', views.GetBoardFile.as_view()),
    path('save-board-file/<str:params>/', views.SaveBoardFile.as_view()),

    # Bids
    path('bid-made/<str:params>/', views.BidMade.as_view()),
    path('use-suggestion/<str:params>/', views.UseSuggestedBid.as_view()),
    path('use-own-bid/<str:params>/', views.UseOwnBid.as_view()),

    # Card play
    path('cardplay/<str:params>/', views.CardPlay.as_view()),
    path('card-played/<str:params>/', views.CardPlayed.as_view()),
    path('claim/<str:params>/', views.Claim.as_view()),
    path('compare-scores/<str:params>/', views.CompareScores.as_view()),

    # Utilities
    path('undo/<str:params>/', views.Undo.as_view()),
    path('versions/', views.Versions.as_view()),
    path('get-parameters/<str:params>/', views.GetParameters.as_view()),
    path('database-update/<str:params>/', views.DatabaseUpdate.as_view()),


    # Messages
    path('message-sent/<str:params>/', views.MessageSent.as_view()),
    path('message-received/<str:params>/', views.MessageReceived.as_view()),
]
