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
    x = room.x
    y = room.y
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'x': x, 'y': y, 'players':players}, safe=True)

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
    nextRoom = None
    if direction == "n":
        nextRoom = room.n_to
    elif direction == "s":
        nextRoom = room.s_to
    elif direction == "e":
        nextRoom = room.e_to
    elif direction == "w":
        nextRoom = room.w_to
    if nextRoom is not None:
        player.currentRoom=nextRoom
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'x': nextRoom.x, 'y': nextRoom.y, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'x': room.x, 'y': room.y, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)

def newmap():
    map = []
    rooms = Room.objects.all().order_by('id')
    for room in rooms:
        id = room.id
        title = room.title
        description = room.description
        n_to = room.n_to.pk if room.n_to is not None else 0
        s_to = room.s_to.pk if room.s_to is not None else 0
        e_to = room.e_to.pk if room.e_to is not None else 0
        w_to = room.w_to.pk if room.w_to is not None else 0
        x = room.x
        y = room.y
        map.append({"id": id, "title": title, "description": description, "n": n_to, "s": s_to, "e": e_to, "w": w_to, "x": x, "y": y})
    return JsonResponse({"map": map}, safe=True)

@csrf_exempt
@api_view(["GET"])
def map(request):
    return newmap()

import random
from collections import deque
@csrf_exempt
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def newworld(request):
    Room.objects.all().delete()
    mx = 30; my = 30 # width and height of the maze
    dx = [0, 1, 0, -1]; dy = [-1, 0, 1, 0] # 4 directions to move in the maze
    # start the maze from a random cell
    cx = random.randint(0, mx - 1); cy = random.randint(0, my - 1)
    room_count = 1
    room = Room(x=cx, y=cy, title=f"Generic Room {room_count}", description="This is a generic room.")
    room.save()
    # maze[cy][cx] = 1
    stack = deque([(room, 0)]) # stack element: (room w/ x&y, direction)

    while room_count < 500 and len(stack) > 0:
        (room, cd) = stack[-1]
        cx, cy = room.x, room.y
        # to prevent zigzags:
        # if changed direction in the last move then cannot change again
        if len(stack) > 2:
            if cd != stack[-2][1]: dirRange = [cd]
            else: dirRange = range(4)
        else: dirRange = range(4)

        # find a new cell to add
        nlst = [] # list of available neighbors
        for i in dirRange:
            nx = cx + dx[i]; ny = cy + dy[i]
            if nx >= 0 and nx < mx and ny >= 0 and ny < my:
                if Room.objects.filter(x=nx, y=ny).exists() is False:
                    ctr = 0 # of occupied neighbors must be 1
                    for j in range(4):
                        ex = nx + dx[j]; ey = ny + dy[j]
                        if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                            if Room.objects.filter(x=ex, y=ey).exists(): ctr += 1
                    if ctr == 1: nlst.append(i)

        # if 1 or more neighbors available then randomly select one and move
        if len(nlst) > 0:
            ir = nlst[random.randint(0, len(nlst) - 1)]
            cx += dx[ir]; cy += dy[ir]
            room_count += 1
            room = Room(x=cx, y=cy, title=f"Generic Room {room_count}", description="This is a generic room.")
            room.save()
            # Possibly where to connect rooms
            dirs = ['s','e','n','w']
            for j in range(4):
                ex = nx + dx[j]; ey = ny + dy[j]
                if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                    neighbor = Room.objects.filter(x=ex, y=ey)
                    if neighbor.exists():
                      room.connectRooms(neighbor[0], dirs[ir])
            stack.append((room, ir))
        else: stack.pop()
    # num_rooms = 100
    # width = 10
    # x = -1 # (this will become 0 on the first step)
    # y = 0
    # room_count = 0
    # # Start generating rooms to the east
    # direction = 1  # 1: east, -1: west
    # # While there are rooms to be created...
    # previous_room = None
    # while room_count < num_rooms:
    #     # Calculate the direction of the room to be created
    #     if direction > 0 and x < width - 1:
    #         room_direction = "e"
    #         x += 1
    #     elif direction < 0 and x > 0:
    #         room_direction = "w"
    #         x -= 1
    #     else:
    #         # If we hit a wall, turn north and reverse direction
    #         room_direction = "n"
    #         y += 1
    #         direction *= -1
    #     # Create a room in the given direction
    #     room = Room(x=x, y=y, title=f"Generic Room {room_count}", description="This is a generic room.")
    #     room.save()
    #     # Connect the new room to the previous room
    #     if previous_room is not None:
    #         previous_room.connectRooms(room, room_direction)
    #         room.save()
    #     # Update iteration variables
    #     previous_room = room
    #     room_count += 1
    return newmap()
