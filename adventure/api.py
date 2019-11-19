from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
import json

# instantiate pusher
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)

# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)

@csrf_exempt
@api_view(["GET"])
def map(request):
    map = []
    rooms = Room.objects.all()
    for room in rooms:
        map.append({"id": room.id, "title": room.title, "description": room.description, "n": room.n_to, "s": room.s_to, "e": room.e_to, "w": room.w_to})
    return JsonResponse({"map": map}, safe=True)

@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAdminUser])
def newworld(request):
    Room.objects.all().delete()

    num_rooms = 100
    width = 10

    x = -1 # (this will become 0 on the first step)
    y = 0
    room_count = 0

    # Start generating rooms to the east
    direction = 1  # 1: east, -1: west


    # While there are rooms to be created...
    previous_room = None
    while room_count < num_rooms:
        # Calculate the direction of the room to be created
        if direction > 0 and x < width - 1:
            room_direction = "e"
            x += 1
        elif direction < 0 and x > 0:
            room_direction = "w"
            x -= 1
        else:
            # If we hit a wall, turn north and reverse direction
            room_direction = "n"
            y += 1
            direction *= -1

        # Create a room in the given direction
        room = Room(x=x, y=y, title=f"Generic Room {room_count}", description="This is a generic room.")
        room.save()

        # Connect the new room to the previous room
        if previous_room is not None:
            previous_room.connect_rooms(room, room_direction)
            room.save()

        # Update iteration variables
        previous_room = room
        room_count += 1
    # ^^ Put generation logic here ^^

    map = []
    rooms = Room.objects.all()
    for room in rooms:
        map.append({"id": room.id, "title": room.title, "description": room.description, "n": room.n_to, "s": room.s_to, "e": room.e_to, "w": room.w_to})
    return JsonResponse({"map": map}, safe=True)
