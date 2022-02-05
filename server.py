import socketio
from aiohttp import web

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)
players = {}
players_counter = 0

@sio.event
async def my_event(sid, data):
    pass


@sio.on('*')
async def catch_all(event, sid, data):
    global players_counter
    players[sid] = data
    players_counter += 1
    if players_counter == 2:
        print(players)
        await sio.emit('my event', players)
        players_counter = 0
    # cur_room = ''
    #
    # for elem in rooms:
    #     if sid in rooms[elem]:
    #         cur_room = elem
    #         break
    #
    # sio.enter_room(sid, cur_room)
    # rooms[cur_room].append(sid)
    # actions[str(rooms[cur_room].index(sid))] = data
    # await sio.emit('my', actions[cur_room])


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
