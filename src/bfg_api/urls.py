"""
To test live server:

https://bidforgame.com/bfg/versions/

"""


# from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    # Static data
    path('static-data/<str:req>/', views.StaticData.as_view()),

    # user login/out
    path('user-login/<str:req>/', views.UserLogin.as_view()),
    path('user-seat/<str:req>/', views.UserSeat.as_view()),
    path('user-logout/<str:req>/', views.UserLogout.as_view()),
    path('user-status/<str:req>/', views.UserStatus.as_view()),

    # REST api
    path('api', views.RoomListApiView.as_view()),
    path('api/<str:room_name>', views.RoomDetailApiView.as_view()),

    # Room
    path('get-user-set-hands/<str:req>/', views.GetUserSetHands.as_view()),
    path('set-user-set-hands/<str:req>/', views.SetUserSetHands.as_view()),

    # Boards
    path('new-board/<str:req>/', views.NewBoard.as_view()),
    path('restart-board/<str:req>/', views.RestartBoard.as_view()),
    path('replay-board/<str:req>/', views.ReplayBoard.as_view()),
    path('room-board/<str:req>/', views.RoomBoard.as_view()),
    path('pbn-board/<str:req>/', views.PbnBoard.as_view()),

    # History
    path('use-history-board/<str:req>/', views.UseHistoryBoard.as_view()),
    path('get-history/<str:req>/', views.GetHistory.as_view()),
    path('rotate-boards/<str:req>/', views.RotateBoards.as_view()),

    # path('save-board-file/<str:req>/', views.SaveBoardFilePut.as_view()),
    path('get-archive-list/<str:req>/', views.GetArchiveList.as_view()),
    path('get-board-file/<str:req>/', views.GetBoardFile.as_view()),
    path('save-board-file/<str:req>/', views.SaveBoardFile.as_view()),

    # Bids
    path('bid-made/<str:req>/', views.BidMade.as_view()),
    path('use-suggestion/<str:req>/', views.UseSuggestedBid.as_view()),
    path('use-own-bid/<str:req>/', views.UseOwnBid.as_view()),

    # Card play
    path('cardplay/<str:req>/', views.CardPlay.as_view()),
    path('card-played/<str:req>/', views.CardPlayed.as_view()),
    path('claim/<str:req>/', views.Claim.as_view()),
    path('compare-scores/<str:req>/', views.CompareScores.as_view()),

    # Utilities
    path('undo/<str:req>/', views.Undo.as_view()),
    path('versions/', views.Versions.as_view()),
    path('get-parameters/<str:req>/', views.GetParameters.as_view()),
    path('database-update/<str:req>/', views.DatabaseUpdate.as_view()),


    # Messages
    path('message-sent/<str:req>/', views.MessageSent.as_view()),
    path('message-received/<str:req>/', views.MessageReceived.as_view()),
]
