from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid

class Room(models.Model):
    title = models.CharField(max_length=50, default="DEFAULT TITLE")
    description = models.CharField(max_length=500, default="DEFAULT DESCRIPTION")
    n_to = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="+", db_column="n_to")
    s_to = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="+", db_column="s_to")
    e_to = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="+", db_column="e_to")
    w_to = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, related_name="+", db_column="w_to")
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    def connectRooms(self, destinationRoom, direction):
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"{direction}_to", destinationRoom)
        setattr(destinationRoom, f"{reverse_dir}_to", self)
        self.save()
        destinationRoom.save()
    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def __str__(self):
        return f"Room {self.id}: {self.title}"


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True, related_name="+", db_column="currentRoom")
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    def initialize(self):
        if self.currentRoom is None:
            self.currentRoom = Room.objects.get(x=0, y=0)
            self.save()
    def room(self):
        if self.currentRoom is not None:
            return self.currentRoom
        else:
            self.initialize()
            return self.room()
    def __str__(self):
        return f"Player {self.id}: {self.user}"

@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()
