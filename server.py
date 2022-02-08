import socketio
from aiohttp import web

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
servers = [{}, {}, {}]
players = {}
players_num = {}
players_counter = 0
maps = ['Level_1', 'Level_1', 'Level_1']

@sio.event
async def not_on_server(sid, data):
    await sio.emit('not_on_server', servers)

@sio.event
async def on_server(sid, data):
    await sio.emit('on_server', [servers[players[sid]], players_num[sid], maps[players[sid]]])

@sio.event
async def now_on_server(sid, data):
    players[sid] = data
    servers[players[sid]][sid] = None
    players_num[sid] = len(servers[players[sid]].keys())
    await sio.emit('on_server', [servers[players[sid]], players_num[sid], maps[players[sid]]])



# @sio.on('*')
# async def catch_all(event, sid, data):
#     global players_counter
#     players[sid] = data
#     players_counter += 1
#     if players_counter == 2:
#         print(players)
#         await sio.emit('my event', players)
#         players_counter = 0
#     # cur_room = ''
#     #
#     # for elem in rooms:
#     #     if sid in rooms[elem]:
#     #         cur_room = elem
#     #         break
#     #
#     # sio.enter_room(sid, cur_room)
#     # rooms[cur_room].append(sid)
#     # actions[str(rooms[cur_room].index(sid))] = data
#     # await sio.emit('my', actions[cur_room])


@sio.event
async def connect(sid, environ, auth):
    players[sid] = [['up']]
    await sio.emit('event', 'something')
    # cur_room = '1'
    # sio.enter_room(sid, cur_room)
    # rooms[cur_room].append(sid)
    # await sio.emit('my', actions[cur_room])
    # print('connect ', sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.event
def my_event(sid, data):
    # handle the message
    return "OK", 123


if __name__ == '__main__':
    web.run_app(app)
