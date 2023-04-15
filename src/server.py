from concurrent import futures
import logging
import signal
import sys

import grpc
import nacl

import eVoting_pb2
import eVoting_pb2_grpc

# HW 2: Public key generation using libsodium dependencies
import secrets
import nacl.utils
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
import pyrqlite.dbapi2 as dbapi2
from math import log

from datetime import datetime, timedelta

class Server:

    registration_table = {}
    challenge_table = {}
    token_table = {}
    election_table = {}


    def check_voter(self, data):
        print(data)

    # HW 2, A: Local Server API (RegisterVoter, UnregisterVoter)
    def RegisterVoter(self, voter: eVoting_pb2.Voter) -> eVoting_pb2.Status:
        index = voter.name
        print(f'1. Registering voter {index}')
        if index not in self.registration_table:
            public_key = VerifyKey(voter.public_key)
            self.registration_table[index] = {"group": voter.group, "public_key": public_key}
            print(f"Voter: {index} is registered")
            return eVoting_pb2.Status(code=0)
        else:
            print(f"Voter {index} is already registered")
            return eVoting_pb2.Status(code=1)
        print("-------------Reg done(2)-------------\n")
        return eVoting_pb2.Status(code=2)

    def UnregisterVoter(self, votername: eVoting_pb2.VoterName) -> eVoting_pb2.Status:
        index = votername.name
        print(f'2. Unregistering voter {index}')
        if index in self.registration_table:
            self.registration_table.pop(index)
            print("Voter is unregistered")
            return eVoting_pb2.Status(code=0)
        else:
            print("Voter doesn't exist")
            return eVoting_pb2.Status(code=1)
        
        return eVoting_pb2.Status(code=2)


# HW 2, B: RPC APIs
class eVotingServicer(eVoting_pb2_grpc.eVotingServicer):

    def __init__(self):
        self.server = Server()
        sign_key = SigningKey.generate()
        with open("private_key", "wb") as f:
            f.write(sign_key.encode())
        verify_key = sign_key.verify_key
        verify_key_bytes = verify_key.encode()

        # HW 2: Verify that register works (register)
        self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        print(self.server.registration_table)
        print("-------------Reg done(0)-------------\n")

        # HW 2: Verify that register works (duplicate)
        self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        print(self.server.registration_table)
        print("-------------Reg done(1)-------------\n")

        # HW 2: Verify that voter works (unregister)
        self.server.UnregisterVoter(eVoting_pb2.VoterName(name="Vidar"))
        print(self.server.registration_table)
        print("-------------UnReg done(0)-------------\n")
        
        # HW 2: Verify that voter works (exists)
        self.server.UnregisterVoter(eVoting_pb2.VoterName(name="Vidar"))
        print(self.server.registration_table)
        print("-------------UnReg done(1)-------------\n")

        # HW 2: Verify that register works (re-register for next part)
        self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        print(self.server.registration_table)
        print("-------------Re-reg done(0)-------------\n")


    # HW2: RPC call
    def PreAuth(self, request, context):
        voter_name = request
        key = voter_name.name
        challenge = secrets.token_bytes(4) # challenge_size = 4
        print(f"1. Received PreAuth. Voter: {key}")
        self.server.challenge_table[key] = challenge # add challenge
        print("-------------PreAuth done-------------\n")
        return eVoting_pb2.Challenge(value = bytes(challenge))

    def Auth(self, request, context):
        # print(f'Name: {request.name.name}')
        # print(f'Response: {request.response.value.decode()}\n')

        auth_req = request
        index = auth_req.name.name
        print(f"2. Received Auth. Name: {index}")
        challenge = self.server.challenge_table[index] # get index
        public_key = self.server.registration_table[index]["public_key"] # get index's public key
        signature = auth_req.response.value

        try:
            public_key.verify(smessage=challenge, signature = signature)
        except:
            return eVoting_pb2.AuthToken(value = bytes("invalid", encoding="utf-8"))

        token = secrets.token_bytes(4)  # token size = 4
        expired = datetime.now()+timedelta(hours=1)
        self.server.token_table[token] = {"expired": expired, "name": index}
        print("-------------Auth done-------------\n")
        return eVoting_pb2.AuthToken(value = bytes(token))

    def CreateElection(self, request, context):
        print("Received CreateElection.")
        print(f'Name: {request.name}')
        print(f'Groups: {request.groups}')
        print(f'Choices: {request.choices}')
        print(f'Time: {datetime.fromtimestamp(request.end_date.seconds)}')
        print(f'Token: {request.token.value}\n')

        try:
            # Status.code=1 : Invalid authentication token
            if request.token.value not in self.server.token_table:
                return eVoting_pb2.Status(code = 1)
            if datetime.now() >= self.server.token_table[request.token.value]["expired"]:
                return eVoting_pb2.Status(code = 1)
            
            
            # Status.code=2 : Missing groups or choices specification 
            if len(request.choices) == 0 or len(request.groups) == 0:
                return eVoting_pb2.Status(code = 2)
            
            # Status.code=0 : Election created successfully
            votes = {}
            for c in request.choices:
                votes[c] = 0;
            self.server.election_table[request.name] = {
                "end_date" : request.end_date.ToDatetime(),\
                "groups" : request.groups,\
                "votes" : votes,\
                "voters" : []}
            return eVoting_pb2.Status(code = 0) 

        # Status.code=3 : Unknown error
        except:
            return eVoting_pb2.Status(code = 3)
        

    def CastVote(self, request, context):
        print("Received CastVote.")
        print(f'Election Name: {request.election_name}')
        print(f'Choice Name: {request.choice_name}')
        print(f'Token: {request.token.value}\n')

        try: 
            # Status.code=1 : Invalid authentication token
            if request.token.value not in self.server.token_table:
                return eVoting_pb2.Status(code = 1)
            if datetime.now() >= self.server.token_table[request.token.value]["expired"]:
                return eVoting_pb2.Status(code = 1)
            
            # Status.code=2 : Invalid election name
            if request.election_name not in self.server.election_table:
                return eVoting_pb2.Status(code = 2)
            if datetime.now() > self.server.election_table[request.election_name]["end_date"]:
                return eVoting_pb2.Status(code = 2)
            
            # Status.code=3 : The voter’s group is not allowed in the election
            name = self.server.token_table[request.token.value]["name"]
            group = self.server.registration_table[name]["group"]
            if group not in self.server.election_table[request.election_name]["groups"]:
                return eVoting_pb2.Status(code = 3)
            
            # Status.code=4 : A previous vote has been cast.
            if name in self.server.election_table[request.election_name]["voters"]:
                return eVoting_pb2.Status(code = 4)
               
            # Status.code=0 : Successful vote
            self.server.election_table[request.election_name]["votes"][request.choice_name] += 1
            self.server.election_table[request.election_name]["voters"].append(name)
            return eVoting_pb2.Status(code = 0)
        
        # Status.code=5 : Unknown error
        except:
            return eVoting_pb2.Status(code = 5)


    def GetResult(self, request, context):
        print("Received GetResult.")
        print(f'Election Name: {request.name}\n')

        result = eVoting_pb2.ElectionResult()
        
        # ElectionResult.status = 1: Non-existent election
        if request.name not in self.server.election_table:
            result.status = 1
            return result
        
        # ElectionResult.status = 2: The election is still ongoing. Election result is not available yet
        if datetime.now() > self.server.election_table[request.name]["end_date"]:
            result.status = 2
            return result
        
        # query is successful: ElectionReuslt.status = 0
        result.status = 0

        for choice, ballot in self.server.election_table[request.name]["votes"].items():
            curVoteCount = result.counts.add()
            curVoteCount.choice_name = choice
            curVoteCount.count = ballot

        return result 
    
    
    

def serve():
    port = '34652'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    eVoting_pb2_grpc.add_eVotingServicer_to_server(
        eVotingServicer(), server)
    server.add_insecure_port('[::]:' + port) 
    server.start()
    print("Server started, listening on " + port, end='\n\n')
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()