# AOT_GameServer

- /join
    - Tokenを返す
- /lobby/{Token : String}
    - 二人目の参加者が来るまで0を返す
    - 二人目の参加者が来たら1or2を返す
- /game/{Token : String}/{UnitNo : int}/{LaneNo : int}
    - /lobby/{Token}の戻り値が1の方はこれを送る
- /game/{Token : String}/GetData
    - Noneか{UnitNo : int} {LaneNo : int}
- /disconnect/{Token : String}
    - OKを返す

