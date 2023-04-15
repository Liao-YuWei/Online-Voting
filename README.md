# Online-Electronic-Voting
- The project of Fault Tolerant Computing in NYCU 111-2

# How to run
1. cd ./Online-Voting/src
2. Launch the server from the terminal: 
``` python server.py ```
3. From another terminal, start the client: 
``` python client.py ```

## How to costomize ip and port?
1. In `src/server.py`, modify the port value in `port = '34652'` and ip in `server.add_insecure_port('[::]:' + port)`.
2. In `src/client.py`, modify the port value in `port = '34652'` and ip in `channel = grpc.insecure_channel('localhost:' + port)`.