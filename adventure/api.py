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

def map(new=False, nodes=[], links=[]):
    if new is True or len(nodes) == 0:
        nodes = []; links = []
        rooms = Room.objects.all().order_by('id')
        for room in rooms:
            nodes.append({
              "id": room.id,
              "x": room.x,
              "y": room.y,
            })
            for d in ['n','s','e','w']:
                if (direction := getattr(room, f"{d}_to")) is not None:
                    links.append({
                      "source": room.id,
                      "target": direction.id
                    })
    return {"nodes": nodes, "links": links}

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
    return JsonResponse({
      'uuid': uuid, 
      'name':user.username, 
      'id':room.id, 
      'title':room.title, 
      'description':room.description, 
      'x': x, 'y': y, 
      'players':players, 
      'map': map()
    }, safe=True)

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
    if direction[0].lower() in ['n', 's', 'e', 'w']:
        nextRoom = getattr(room, f"{direction[0]}_to")
    if nextRoom is not None:
        player.currentRoom = nextRoom
        player.save()
        players = nextRoom.playerNames(player_id)
        # currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'id':nextRoom.id, 'title':nextRoom.title, 'description':nextRoom.description, 'x': nextRoom.x, 'y': nextRoom.y, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'x': room.x, 'y': room.y, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    return JsonResponse({'error':"Not yet implemented"}, safe=True, status=500)

# References for nameit() in newworld
# 25 nouns
nouns = ['Maze of the Ebon Wolf', 'Catacombs of Deaths Tiger', 'Burrows of the Shunned Tiger', 'Caverns of the Cold Arachnid', 'Thundering Dungeon',
    'Voiceless Whimpers Grotto', 'Unknown Catacombs', 'Black Mountain Maze', 'Abysmal Haunt', 'Vault of the Destroyed Wizard',
    'Burning Lair', 'Caverns of the Cruel Dragon', 'Black Widow', 'Burned Delves', 'Sterile Chambers',
    'Eternal Rest Cells', 'Chambers of the Black Priest', 'Lair of the Golden Priest', 'Lair of the Spirit Giant', 'Obliterated Maze',
    'Dying Crypt', 'Destroyed Tombs', 'Catacombs of the Savage Arachnid', 'Pits of the Unspoken Basilisk', 'Vault of the Frozen Goblin']
# 25 adjectives
adjs = ['The', 'The', 'The', 'The', 'The',
    'The', 'The', 'The', 'The', 'The',
    'The', 'The', 'The', 'The', 'The',
    'The', 'The', 'The', 'The', 'The'
]
# 100 sentences
descriptions = ['As the door opens, it scrapes up frost from a floor covered in ice. The room before you looks like an ice cave. A tunnel wends its way through solid ice, and huge icicles and pillars of frozen water block your vision of its farthest reaches. ',
    'This room is a small antechamber before two titanic bronze doors. Each stands 20 feet tall and is about 7 feet wide.',
    'You inhale a briny smell like the sea as you crack open the door to this chamber. Within you spy the source of the scent: a dark and still pool of brackish water within a low circular wall.',
    'You enter a small room and your steps echo. Looking about, you\'re uncertain why, but then a wall vanishes and reveals an enormous chamber. The wall was an illusion and whoever cast it must be nearby! ',
    'This room smells strange, no doubt due to the weird sheets of black slime that drip from cracks in the ceiling and spread across the floor. The slime seeps from the shattered stone of the ceiling at a snails crawl, ',
    'A wall that holds a seat with a hole in it is in this chamber. It\'s a privy! The noisome stench from the hole leads you to believe that the privy sees regular use. ',
    'Burning torches in iron sconces line the walls of this room, lighting it brilliantly. At the room\'s center lies a squat stone altar, its top covered in recently spilled blood.',
    'This small room contains several pieces of well-polished wood furniture. Eight ornate, high-backed chairs surround a long oval table, and a side table stands next to the far exit.',
    'The door to this room swings open easily on well-oiled hinges. Beyond it you see that the chamber walls have been disguised by wood paneling, and the stone ceiling and floor are hidden by bright marble tiles.',
    'Rats inside the room shriek when they hear the door open, then they run in all directions from a putrid corpse lying in the center of the floor. ',
    'The door creaks open, which somewhat overshadows the sound of bubbling liquid. Before you is a room about which alchemists dream. ',
    'This hall stinks with the wet, pungent scent of mildew. Black mold grows in tangled veins across the walls and parts of the floor. Despite the smell, it looks like it might be safe to travel through.',
    'A pit yawns open before you just on the other side of the door\'s threshold. The entire floor of the room has fallen into a second room beneath it.',
    'This room is shattered. A huge crevasse shears the chamber in half, and the ground and ceilings are tilted away from it. It\'s as though the room was gripped in two enormous hands and broken like a loaf of bread.',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond. The room from which they came seems barren... at first glance. ',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond.',
    'You open the door to what must be a combat training room. Rough fighting circles are scratched into the surface of the floor. Wooden fighting dummies stand waiting for someone to attack them.',
    'You peer through the open doorway into a broad, pillared hall. The columns of stone are carved as tree trunks and seem placed at random like trees in a forest.',
    'A horrendous, overwhelming stench wafts from the room before you. Small cages containing small animals and large insects line the walls. Some of the creatures look sickly and alive but most are clearly dead. ',
    'Many doors fill the room ahead. Doors of varied shape, size, and design are set in every wall and even the ceiling and floor.',
    'This hall is choked with corpses. The bodies of orcs and ogres lie in tangled heaps where they died, and the floor is sticky with dried blood.',
    'A stone throne stands on a foot-high circular dais in the center of this cold chamber. ',
    'This room is a tomb. Stone sarcophagi stand in five rows of three, each carved with the visage of a warrior lying in state. In their center, one sarcophagus stands taller than the rest.',
    'You peer into this room and spot the white orb of a skull lying on the floor. Suddenly a stone falls from the ceiling and smashes the skull to pieces.',
    'You feel a sense of foreboding upon peering into this cavernous chamber. At its center lies a low heap of refuse, rubble, and bones atop which sit several huge broken eggshells.',
    'Several round pits lie in the floor of the room before you. Spaced roughly equally apart, each is about 15 feet in diameter and appears about 20 feet deep.',
    'This chamber holds one occupant: the statue of a male figure with elven features but the broad, muscular body of a hale human. It kneels on the floor as though fallen to that posture.',
    'You\'ve opened the door to a torture chamber. Several devices of degradation, pain, and death stand about the room, all of them showing signs of regular use.',
    'You open the door and a gout of flame rushes at your face. A wave of heat strikes you at the same time and light fills the hall. The room beyond the door is ablaze! An inferno engulfs the place, clinging to bare rock and burning without fuel.',
    'A cluster of low crates surrounds a barrel in the center of this chamber. Atop the barrel lies a stack of copper coins and two stacks of cards, one face up. Meanwhile, atop each crate rests a fan of five face-down playing cards.',
    'This room is hung with hundreds of dusty tapestries. All show signs of wear: moth holes, scorch marks, dark stains, and the damage of years of neglect.',
    'You round the corner to see a ghastly scene. A semitranslucent figure hangs in the air, studded with crossbow bolts and with blood pouring from every wound. It reaches toward you in a pleading gesture, points to the walls on either side of the room, and then vanishes.',
    'A strange ceiling is the focal point of the room before you. It\'s honeycombed with hundreds of holes about as wide as your head.',
    'A glow escapes this room through its open doorways. The masonry between every stone emanates an unnatural orange radiance.',
    'Many small desks with high-backed chairs stand in three long rows in this room. Each desk has an inkwell, book stand, and a partially melted candle in a rusting tin candleholder. Everything is covered with dust. ',
    'A pungent, earthy odor greets you as you pull open the door and peer into this room. Mushrooms grow in clusters of hundreds all over the floor. Looking into the room is like looking down on a forest.',
    'As the door opens, it scrapes up frost from a floor covered in ice. The room before you looks like an ice cave. A tunnel wends its way through solid ice, and huge icicles and pillars of frozen water block your vision of its farthest reaches. ',
    'This room is a small antechamber before two titanic bronze doors. Each stands 20 feet tall and is about 7 feet wide.',
    'You inhale a briny smell like the sea as you crack open the door to this chamber. Within you spy the source of the scent: a dark and still pool of brackish water within a low circular wall.',
    'You enter a small room and your steps echo. Looking about, you\'re uncertain why, but then a wall vanishes and reveals an enormous chamber. The wall was an illusion and whoever cast it must be nearby! ',
    'This room smells strange, no doubt due to the weird sheets of black slime that drip from cracks in the ceiling and spread across the floor. The slime seeps from the shattered stone of the ceiling at a snails crawl, ',
    'A wall that holds a seat with a hole in it is in this chamber. It\'s a privy! The noisome stench from the hole leads you to believe that the privy sees regular use. ',
    'Burning torches in iron sconces line the walls of this room, lighting it brilliantly. At the room\'s center lies a squat stone altar, its top covered in recently spilled blood.',
    'This small room contains several pieces of well-polished wood furniture. Eight ornate, high-backed chairs surround a long oval table, and a side table stands next to the far exit.',
    'The door to this room swings open easily on well-oiled hinges. Beyond it you see that the chamber walls have been disguised by wood paneling, and the stone ceiling and floor are hidden by bright marble tiles.',
    'Rats inside the room shriek when they hear the door open, then they run in all directions from a putrid corpse lying in the center of the floor. ',
    'The door creaks open, which somewhat overshadows the sound of bubbling liquid. Before you is a room about which alchemists dream. ',
    'This hall stinks with the wet, pungent scent of mildew. Black mold grows in tangled veins across the walls and parts of the floor. Despite the smell, it looks like it might be safe to travel through.',
    'A pit yawns open before you just on the other side of the door\'s threshold. The entire floor of the room has fallen into a second room beneath it.',
    'This room is shattered. A huge crevasse shears the chamber in half, and the ground and ceilings are tilted away from it. It\'s as though the room was gripped in two enormous hands and broken like a loaf of bread.',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond. The room from which they came seems barren... at first glance. ',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond.',
    'You open the door to what must be a combat training room. Rough fighting circles are scratched into the surface of the floor. Wooden fighting dummies stand waiting for someone to attack them.',
    'You peer through the open doorway into a broad, pillared hall. The columns of stone are carved as tree trunks and seem placed at random like trees in a forest.',
    'A horrendous, overwhelming stench wafts from the room before you. Small cages containing small animals and large insects line the walls. Some of the creatures look sickly and alive but most are clearly dead. ',
    'Many doors fill the room ahead. Doors of varied shape, size, and design are set in every wall and even the ceiling and floor.',
    'This hall is choked with corpses. The bodies of orcs and ogres lie in tangled heaps where they died, and the floor is sticky with dried blood.',
    'A stone throne stands on a foot-high circular dais in the center of this cold chamber. ',
    'This room is hung with hundreds of dusty tapestries. All show signs of wear: moth holes, scorch marks, dark stains, and the damage of years of neglect.',
    'You round the corner to see a ghastly scene. A semitranslucent figure hangs in the air, studded with crossbow bolts and with blood pouring from every wound. It reaches toward you in a pleading gesture, points to the walls on either side of the room, and then vanishes.',
    'A strange ceiling is the focal point of the room before you. It\'s honeycombed with hundreds of holes about as wide as your head.',
    'A glow escapes this room through its open doorways. The masonry between every stone emanates an unnatural orange radiance.',
    'Many small desks with high-backed chairs stand in three long rows in this room. Each desk has an inkwell, book stand, and a partially melted candle in a rusting tin candleholder. Everything is covered with dust. ',
    'A pungent, earthy odor greets you as you pull open the door and peer into this room. Mushrooms grow in clusters of hundreds all over the floor. Looking into the room is like looking down on a forest.',
    'As the door opens, it scrapes up frost from a floor covered in ice. The room before you looks like an ice cave. A tunnel wends its way through solid ice, and huge icicles and pillars of frozen water block your vision of its farthest reaches. ',
    'This room is a small antechamber before two titanic bronze doors. Each stands 20 feet tall and is about 7 feet wide.',
    'You inhale a briny smell like the sea as you crack open the door to this chamber. Within you spy the source of the scent: a dark and still pool of brackish water within a low circular wall.',
    'You enter a small room and your steps echo. Looking about, you\'re uncertain why, but then a wall vanishes and reveals an enormous chamber. The wall was an illusion and whoever cast it must be nearby! ',
    'This room smells strange, no doubt due to the weird sheets of black slime that drip from cracks in the ceiling and spread across the floor. The slime seeps from the shattered stone of the ceiling at a snails crawl, ',
    'A wall that holds a seat with a hole in it is in this chamber. It\'s a privy! The noisome stench from the hole leads you to believe that the privy sees regular use. ',
    'Burning torches in iron sconces line the walls of this room, lighting it brilliantly. At the room\'s center lies a squat stone altar, its top covered in recently spilled blood.',
    'This small room contains several pieces of well-polished wood furniture. Eight ornate, high-backed chairs surround a long oval table, and a side table stands next to the far exit.',
    'The door to this room swings open easily on well-oiled hinges. Beyond it you see that the chamber walls have been disguised by wood paneling, and the stone ceiling and floor are hidden by bright marble tiles.',
    'Rats inside the room shriek when they hear the door open, then they run in all directions from a putrid corpse lying in the center of the floor. ',
    'The door creaks open, which somewhat overshadows the sound of bubbling liquid. Before you is a room about which alchemists dream. ',
    'This hall stinks with the wet, pungent scent of mildew. Black mold grows in tangled veins across the walls and parts of the floor. Despite the smell, it looks like it might be safe to travel through.',
    'A pit yawns open before you just on the other side of the door\'s threshold. The entire floor of the room has fallen into a second room beneath it.',
    'This room is shattered. A huge crevasse shears the chamber in half, and the ground and ceilings are tilted away from it. It\'s as though the room was gripped in two enormous hands and broken like a loaf of bread.',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond. The room from which they came seems barren... at first glance. ',
    'A flurry of bats suddenly flaps through the doorway, their screeching barely audible as they careen past your heads. They flap past you into the rooms and halls beyond.',
    'You open the door to what must be a combat training room. Rough fighting circles are scratched into the surface of the floor. Wooden fighting dummies stand waiting for someone to attack them.',
    'You peer through the open doorway into a broad, pillared hall. The columns of stone are carved as tree trunks and seem placed at random like trees in a forest.',
    'A horrendous, overwhelming stench wafts from the room before you. Small cages containing small animals and large insects line the walls. Some of the creatures look sickly and alive but most are clearly dead. ',
    'Many doors fill the room ahead. Doors of varied shape, size, and design are set in every wall and even the ceiling and floor.',
    'This hall is choked with corpses. The bodies of orcs and ogres lie in tangled heaps where they died, and the floor is sticky with dried blood.',
    'A stone throne stands on a foot-high circular dais in the center of this cold chamber. ',
    'This room is a tomb. Stone sarcophagi stand in five rows of three, each carved with the visage of a warrior lying in state. In their center, one sarcophagus stands taller than the rest.',
    'You peer into this room and spot the white orb of a skull lying on the floor. Suddenly a stone falls from the ceiling and smashes the skull to pieces.',
    'You feel a sense of foreboding upon peering into this cavernous chamber. At its center lies a low heap of refuse, rubble, and bones atop which sit several huge broken eggshells.',
    'Several round pits lie in the floor of the room before you. Spaced roughly equally apart, each is about 15 feet in diameter and appears about 20 feet deep.',
    'This chamber holds one occupant: the statue of a male figure with elven features but the broad, muscular body of a hale human. It kneels on the floor as though fallen to that posture.',
    'You\'ve opened the door to a torture chamber. Several devices of degradation, pain, and death stand about the room, all of them showing signs of regular use.',
    'You open the door and a gout of flame rushes at your face. A wave of heat strikes you at the same time and light fills the hall. The room beyond the door is ablaze! An inferno engulfs the place, clinging to bare rock and burning without fuel.',
    'A cluster of low crates surrounds a barrel in the center of this chamber. Atop the barrel lies a stack of copper coins and two stacks of cards, one face up. Meanwhile, atop each crate rests a fan of five face-down playing cards.',
    'This room is hung with hundreds of dusty tapestries. All show signs of wear: moth holes, scorch marks, dark stains, and the damage of years of neglect.',
    'You round the corner to see a ghastly scene. A semitranslucent figure hangs in the air, studded with crossbow bolts and with blood pouring from every wound. It reaches toward you in a pleading gesture, points to the walls on either side of the room, and then vanishes.',
    'A strange ceiling is the focal point of the room before you. It\'s honeycombed with hundreds of holes about as wide as your head.',
    'A glow escapes this room through its open doorways. The masonry between every stone emanates an unnatural orange radiance.',
    'Many small desks with high-backed chairs stand in three long rows in this room. Each desk has an inkwell, book stand, and a partially melted candle in a rusting tin candleholder. Everything is covered with dust. ',
    'A pungent, earthy odor greets you as you pull open the door and peer into this room. Mushrooms grow in clusters of hundreds all over the floor. Looking into the room is like looking down on a forest.',
    ]
rooms = []
# create 625 room names
for noun in nouns:
    for adj in adjs:
        rooms.append(adj + ' ' + noun)

import random
from collections import deque
@csrf_exempt
@api_view(["PUT"])
@permission_classes([IsAdminUser])
def newmap(request):
    def nameit():
        return {"title": random.choice(rooms), "description": random.choice(descriptions)}

    Room.objects.all().delete()
    mx = 30; my = 30 # width and height of the maze
    dx = [0, 1, 0, -1]; dy = [-1, 0, 1, 0] # 4 directions to move in the maze
    # start the maze from a random cell
    cx = random.randint(0, mx - 1); cy = random.randint(0, my - 1)
    room_count = 1
    room = Room(x=cx, y=cy, **nameit())
    room.save()
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
            room = Room(x=cx, y=cy, **nameit())
            room.save()
            # Possibly where to connect rooms
            dirs = ['s','w','n','e']
            for j in range(4):
                ex = cx + dx[j]; ey = cy + dy[j]
                if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                    neighbor = Room.objects.filter(x=ex, y=ey)
                    if neighbor.exists():
                      room.connectRooms(neighbor[0], dirs[ir])
            stack.append((room, ir))
        else: stack.pop()

    return JsonResponse({"map": map(new=True)}, safe=True)
