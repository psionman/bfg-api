from django.db import models
import json


class Room(models.Model):
    name = models.CharField(max_length=180)
    last_task = models.CharField(max_length=32, blank=True)
    last_data = models.CharField(max_length=64, blank=True)
    board_number = models.IntegerField(default=0)
    set_hands = models.CharField(null=True, blank=True,
                                 max_length=512, default=json.dumps([]))
    use_set_hands = models.BooleanField(default=False)
    display_hand_type = models.BooleanField(default=False)
    own_bid = models.CharField(max_length=32, blank=True)
    suggested_bid = models.CharField(max_length=32, blank=True)
    board_pbn = models.CharField(null=True, blank=True,
                                 max_length=512, default='')
    board = models.TextField(blank=True)
    archive = models.TextField(blank=True)
    saved_boards = models.TextField(blank=True, default=json.dumps([]))

    def __str__(self):
        return f'Room({self.name} set_hands={self.set_hands})'
