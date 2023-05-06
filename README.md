# Online-Electronic-Voting
- The project of Fault Tolerant Computing in NYCU 111-2

# How to run
You need 5 terminals.  
1. Start a single rqlite node:  
    `cd rqlite-v7.3.2-linux-amd64/`  
    `./rqlited -node-id 1 node.1`

2. Forming a database cluster with 2 nodes:  
    `cd rqlite-v7.3.2-linux-amd64/`  
    `./rqlited -node-id 2 -http-addr localhost:4003 -raft-addr localhost:4004 -join http://localhost:4001 node.2`

3. Launch backup server:  
    `cd src/`  
    `python3 server.py 55556 4001`

4. Launch primary server:  
    `cd src/`  
    `python3 server.py 55555 4003`

5. Launch client:  
    `cd src/`  
    `python3 client.py`  
    Do the voting in client.py.