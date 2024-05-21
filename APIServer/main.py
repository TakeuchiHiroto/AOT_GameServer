from fastapi import FastAPI
import uvicorn
from typing import Optional
from pydantic import BaseModel
import uuid
import argparse

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
    join_player = 0

    is_SetGameData = False

    game_data = GameData()

    def __init__(self, token : str):
        self.token = token
        self.player1 = False
        self.player2 = False
        self.join_player = 0
        self.game_data.UnitNo = -1
        self.game_data.LaneNo = -1
        self.is_SetGameData = False


Lobbys = []

@app.get("/join")
def join():
    if len(Lobbys) == 0:
        token = str(uuid.uuid4())
        Lobbys.append(Lobby(token))
    
    last_lobby = Lobbys[-1]

    if last_lobby.player1 == False: # プレイヤー１がいない場合
        last_lobby.player1 = True
        return {"token": last_lobby.token}
    elif last_lobby.player2 == False: # プレイヤー２がいない場合
        last_lobby.player2 = True
        return {"token": last_lobby.token}
    
    # どちらもいる場合(新しくロビーを作成する)
    token = str(uuid.uuid4())
    Lobbys.append(Lobby(token))
    Lobbys[-1].player1 = True
    return {"token": token}


@app.get("/lobby/{token}")
def lobby(token: str):
    try:
        for lobby in Lobbys:
            print(lobby.token + " " + token) 
            if lobby.token == token:
                print(token)
                if lobby.player1 == True and lobby.player2 == True:
                    if lobby.join_player == 0:
                        lobby.join_player = 1
                        print(lobby.join_player)
                        return {"player": 1}
                    elif lobby.join_player == 1:
                        lobby.join_player = 2
                        print(lobby.join_player)
                        return {"player": 2}
                else:
                    return {"player": 0}
        return {"status": "TimeOut"}
    except:
        return {"error": "Invalid token"}

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