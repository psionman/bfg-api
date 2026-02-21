"""
BFG API URL configuration.

Live server health/version check:
    https://bidforgame.com/bfg/versions/

Conventions:
- All state-mutating endpoints use POST
- Request bodies are JSON
- CSRF protection is enabled for all POST requests
- Client must call /ensure-csrf/ once before POSTing
"""


from django.urls import path
from . import views


urlpatterns = [
    # Bootstrap / Static
    path('ensure-csrf/', views.ensure_csrf),
    path('static-data/', views.StaticData.as_view()),
    path('amsterdam/', views.debug_view.as_view()),

    # User session
    path('user-login/', views.UserLogin.as_view()),
    path('user-seat/', views.UserSeat.as_view()),
    path('user-logout/', views.UserLogout.as_view()),
    path('user-status/', views.UserStatus.as_view()),

    # Room / Setup
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

    # Bidding
    path('bid-made/', views.BidMade.as_view()),
    path('use-suggestion/', views.UseSuggestedBid.as_view()),
    path('use-own-bid/', views.UseOwnBid.as_view()),

    # Card play
    path('cardplay/', views.CardPlay.as_view()),
    path('card-played/', views.CardPlayed.as_view()),
    path('claim/', views.Claim.as_view()),
    path('compare-scores/', views.CompareScores.as_view()),

    # Utilities / Admin
    path('undo/', views.Undo.as_view()),
    path('database-update/', views.DatabaseUpdate.as_view()),


    # Messaging
    path('message-sent/', views.MessageSent.as_view()),
    path('message-received/', views.MessageReceived.as_view()),
]
