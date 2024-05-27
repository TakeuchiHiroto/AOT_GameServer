from fastapi import FastAPI
import uvicorn
from typing import Optional
from pydantic import BaseModel
import uuid
import argparse
import time

parser = argparse.ArgumentParser(description="Run FastAPI application")
parser.add_argument('-p', '--port', default=8000, type=int, help="Port to run the application on")
args = parser.parse_args()

app = FastAPI()

class GameData():
    UnitNo: int
    LaneNo: int

class Lobby:
    token = ""
    player1 = False
    player2 = False

    player1_token = ""
    player2_token = ""

    join_player = 0

    last_time = time.time()

    is_SetGameData = False

    turn_end_flag = False

    player1_ready = False
    player2_ready = False

    game_data = GameData()
    def __init__(self, token : str):
        self.token = token
        self.player1 = False
        self.player2 = False
        self.join_player = 0
        self.game_data.UnitNo = -1
        self.game_data.LaneNo = -1
        self.is_SetGameData = False
        self.last_time = time.time()
        self.turn_end_flag = False
        self.player1_token = str(uuid.uuid4())
        self.player2_token = str(uuid.uuid4())
        self.player1_ready = False
        self.player2_ready = False
        


Lobbys = []
last_time = time.time()

@app.get("/join")
def join():
    global last_time
    global Lobbys

    # 最後のロビーが作成されてから10分以上経過していたら、全てのロビーを削除する
    if time.time() - last_time > 600:
        Lobbys = []
    last_time = time.time()

    if len(Lobbys) == 0:
        token = str(uuid.uuid4())
        Lobbys.append(Lobby(token))
    
    last_lobby = Lobbys[-1]

    if last_lobby.player1 == False: # プレイヤー１がいない場合
        last_lobby.player1 = True
        return {"token": last_lobby.player1_token}
    elif last_lobby.player2 == False: # プレイヤー２がいない場合
        last_lobby.player2 = True
        return {"token": last_lobby.player2_token}
    else:
        # どちらもいる場合(新しくロビーを作成する)
        token = str(uuid.uuid4())
        Lobbys.append(Lobby(token))
        Lobbys[-1].player1 = True
        return {"token": Lobbys[-1].player1_token}


@app.get("/lobby/{token}")
def lobby(token: str):
    try:
        for lobby in Lobbys:
            print(lobby.player1_token + ":" + lobby.player2_token + " : " + token) 
            if lobby.player1_token == token:
                # ロビーにプレイヤー１が最後にアクセスされてから20秒以上経過していたら、ロビーを削除する
                if time.time() - lobby.last_time > 20:
                    Lobbys.remove(lobby)
                    return {"status": "TimeOut"}
            lobby.last_time = time.time()

            if lobby.player1_token == token:
                lobby.join_player = 1
                lobby.last_time = time.time()
                return {"player" : 1}
            elif lobby.player2_token == token:
                lobby.join_player = 2
                lobby.last_time = time.time()
                return {"player" : 2}
        return {"status": "TimeOut"}
    except:
        return {"error": "Invalid token"}

@app.get("/lobby/{token}/isStart")
def isStart(token: str):
    for lobby in Lobbys:
        if lobby.token == token:
            if lobby.join_player >= 2:
                return {"status": "OK"}
            else:
                return {"status": "NG"}
    return {"status": "TimeOut"}

@app.get("/lobby/{token}/isPlayerStart")
def isRedey(token: str):
    for lobby in Lobbys:
        if lobby.player1_token == token:
            lobby.player1_ready = True
            return {"status": "OK"}
        if lobby.player2_token == token and lobby.player1_ready:
            lobby.player2_ready = True
            return {"status": "OK"}
        
    return {"status": "NG"}


@app.get("/lobby/get_token/{token}")
def getLobbyToken(token: str):
    for lobby in Lobbys:
        if lobby.player1_token == token:
            return {"token": lobby.token}
        elif lobby.player2_token == token:
            return {"token": lobby.token}
    return {"status": "TimeOut"}

@app.get("/game/{token}/{unit_no}/{lane_no}")
def game(token: str, unit_no: int, lane_no: int):
    for lobby in Lobbys:
        if lobby.token == token:
            if(lobby.is_SetGameData):
                return {"status": "NG"}
            lobby.game_data.UnitNo = unit_no
            lobby.game_data.LaneNo = lane_no
            lobby.is_SetGameData = True
            return {"status": "OK"}
    return {"status": "TimeOut"}

@app.get("/game/{token}/TurnEnd")
def turn_end(token: str):
    for lobby in Lobbys:
        if lobby.token == token:
            lobby.is_SetGameData = False
            lobby.turn_end_flag = True
            return {"status": "OK"}
    return {"status": "TimeOut"}

@app.get("/game/{token}/getTurnEnd")
def get_turn_end(token: str):
    for lobby in Lobbys:
        if lobby.token == token:
            if lobby.turn_end_flag:
                lobby.turn_end_flag = False
                return {"status": "OK"}
            else:
                return {"status": "NG"}
    return {"status": "TimeOut"}

@app.get("/game/{token}/get")
def get_data(token: str):
    for lobby in Lobbys:
        if lobby.token == token:
            if(lobby.is_SetGameData):
                lobby.is_SetGameData = False
                return lobby.game_data
            else:
                return  {"status": "Null"}
    else:
        return  {"status": "TimeOut"}

@app.get("/disconnect/{token}")
def disconnect(token: str):
    for i in range(len(Lobbys)):
        if Lobbys[i].token == token:
            Lobbys.pop(i)
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=args.port)