# Fault Tolerant Computing Homework 1
> Members: 廖昱瑋、蔡品緣、謝旻紜、韓明洋

## Source Code
https://github.com/Liao-YuWei/Online-Voting  

## How to run?
1. Run `python ./src/server.py`
2. Run `python ./src/client.py`

## How to costomize ip and port?
1. In `src/server.py`, modify the port value in `port = '34652'` and ip in `server.add_insecure_port('[::]:' + port)`.
2. In `src/client.py`, modify the port value in `port = '34652'` and ip in `channel = grpc.insecure_channel('localhost:' + port)`.

## Implementation
We defined the following RPC functions in this homework
```
rpc PreAuth (VoterName) returns (Challenge);
rpc Auth (AuthRequest) returns (AuthToken);
rpc CreateElection (Election) returns (Status);
rpc CastVote (Vote) returns (Status);
rpc GetResult(ElectionName) returns (ElectionResult);
```
Then, call these APIs with some dummy values.

## Sample Result
* Server Side  
![](https://i.imgur.com/HpBQlp8.png)
* Client Side  
![](https://i.imgur.com/AdUK2Vt.png)

## What will happen when a gRPC call ecounters network connection problems?
We tested it by typing wrong ip address in client side intentionally. The error message popped out as below. The TCP failed to build connection by doing handshake.
![](https://i.imgur.com/u28rQhw.png)