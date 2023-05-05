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

from Db import Db

class Server:

    def __init__(self, db_port):
        self.db_ip = 'localhost'
        self.db_port = db_port
        # self.db_obj = Db(self.db_ip, self.db_port)
        self.registration_table = {}
        self.challenge_table = {}
        self.token_table = {}
        self.election_table = {}
        


    def check_voter(self, data):
        print(data)

    def get_registers_name_list(self):
        db = Db(self.db_ip, self.db_port)
        return db.get_registers_name_list()
        # return self.db_obj.get_registers_name_list()


    def add_register(self, index, group, public_key):
        db = Db(self.db_ip, self.db_port)
        status = db.add_register(index, group, public_key)
        return status
        # return self.db_obj.add_register(index, group, public_key)

    def delete_register(self, index):
        db = Db(self.db_ip, self.db_port)
        status = db.delete_register(index)
        return status
        # return self.db_obj.delete_register(index, group, public_key)

    def add_challenge(self, index, challenge):
        db = Db(self.db_ip, self.db_port)
        db.add_challenge(index , challenge)
        # self.db_obj.add_challenge(index, challenge)

    def get_challenge(self, index):
        db = Db(self.db_ip, self.db_port)
        return db.get_challenge(index)
        # return self.db_obj.get_challenge(index)

    def get_register_publicKey(self, index):
        db = Db(self.db_ip, self.db_port)
        group , public_key = db.get_register(index)
        return public_key
        # group, public_key = self.db_obj.get_register(index)
        # return public_key
    
    def add_token(self, index, name, expired_time):
        db = Db(self.db_ip, self.db_port)
        db.add_token(index, expired_time, name)
        # self.db_obj.add_token(index, expired_time, name)

    def is_Valid_token(self, index):
        db = Db(self.db_ip, self.db_port)
        expired , name = db.get_token(index)
        return datetime.now() < expired
        # expired , name = self.db_obj.get_token(index)
        # return datetime.now() < expired
    
    def add_election(self , election):
        db = Db(self.db_ip, self.db_port)
        due = election.end_date.ToDatetime()
        db.add_election(election.name , due , election.groups , election.choices)
        # due = election.end_date.ToDatetime()
        # self.db_obj.add_election(election.name , due , election.groups , election.choices)
    
    def isDue_election(self,index):
        db = Db(self.db_ip, self.db_port)
        election = db.get_election(index)
        return datetime.now() > election["end_date"]
        # return datetime.now() > self.db_obj.get_election(index)["end_date"]
        

    def add_vote(self, index, choice, voter_name):
        db = Db(self.db_ip, self.db_port)
        db.add_vote(index, choice, voter_name)
        # self.db_obj.add_vote(index, choice, voter_name)
        
    
    def repeated_vote(self, election_name, voter_name):
        db = Db(self.db_ip, self.db_port)
        election = db.get_election(election_name)
        return voter_name in election["voters"]
        # return voter_name in self.db_obj.get_election(election_name)["voters"]

    def valid_group(self, election_name, group):
        db = Db(self.db_ip, self.db_port)
        election = db.get_election(election_name)
        return group in election['groups']
        # return group in self.db_obj.get_election(election_name)["groups"]
    
    def get_voter_name(self, token):
        db = Db(self.db_ip, self.db_port)
        expired, name = db.get_token(token)
        # expired, name = self.db_obj.get_token(token)
        return name

    def get_voter_group(self, voter_name):
        db = Db(self.db_ip, self.db_port)
        group, public_key = db.get_register(voter_name)
        #print('group is public key is',voter_name)
        # group, public_key = self.db._obj.get_register(voter_name)
        return group

    def existed_election(self, index):
        db = Db(self.db_ip, self.db_port)
        return index in db.get_all_elections()
        # return index in self.db_obj.get_all_elections()

    def due_election(self, index):
        db = Db(self.db_ip, self.db_port)
        election = db.get_election(index)
        return datetime.now() > election["end_date"]
        #return datetime.now() > db.get_election(index)["end_date"]
        # return datetime.now() > self.db_obj.get_election(index)["end_date"]

    def get_result(self, index):
        db = Db(self.db_ip, self.db_port)
        return db.get_election(index)["votes"]
        # return self.db_obj.get_election(index)["votes"]




    # HW 2, A: Local Server API (RegisterVoter, UnregisterVoter)
    def RegisterVoter(self, voter: eVoting_pb2.Voter) -> eVoting_pb2.Status:
        try:
            index = voter.name
            print(f'1. Registering voter {index}')
            public_key = VerifyKey(voter.public_key)
            # self.registration_table[index] = {"group": voter.group, "public_key": public_key}
            status_code = self.add_register(index, voter.group, public_key)
            if status_code == 0:
                print(f"Voter: {index} is registered")
                return eVoting_pb2.Status(code=0)
            elif status_code == 1:
                print(f"Voter {index} is already registered")
                return eVoting_pb2.Status(code=1)
        except:
            print(f"Voter register: undefined error!")
            return eVoting_pb2.Status(code=2)

    def UnregisterVoter(self, votername: eVoting_pb2.VoterName) -> eVoting_pb2.Status:
        try:
            index = votername.name
            print(f'2. Unregistering voter {index}')
            status_code = self.delete_register(index)
            if status_code == 0:
                print("Voter is unregistered")
                return eVoting_pb2.Status(code=0)
            elif status_code == 1:
                print("Voter doesn't exist")
                return eVoting_pb2.Status(code=1)
        except:
            print(f"Voter unregister: undefined error!")
            return eVoting_pb2.Status(code=2)
        

# HW 2, B: RPC APIs
class eVotingServicer(eVoting_pb2_grpc.eVotingServicer):

    def __init__(self, db_port):
        self.server = Server(db_port)
        sign_key = SigningKey.generate()
        # with open("private_key_vidar", "wb") as f:
        #     f.write(sign_key.encode())
        verify_key = sign_key.verify_key
        verify_key_bytes = verify_key.encode()
        # with open("public_key", "rb") as f:
        #     verify_key_bytes = f.read()

        # Voter 1: Vidar
        # HW 2: Verify that register works (register)
        reg_response = self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        if reg_response.code == 0:
            with open("private_key_vidar", "wb") as f:
                f.write(sign_key.encode()) 
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------Reg done(0)-------------\n")

        # HW 2: Verify that register works (duplicate)
        reg_response = self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        print(reg_response.code)
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------Reg done(1)-------------\n")

        # HW 2: Verify that voter works (unregister)
        reg_response = self.server.UnregisterVoter(eVoting_pb2.VoterName(name="Vidar"))
        print(reg_response.code)
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------UnReg done(0)-------------\n")
        
        # HW 2: Verify that voter works (exists)
        reg_response = self.server.UnregisterVoter(eVoting_pb2.VoterName(name="Vidar"))
        print(reg_response.code)
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------UnReg done(1)-------------\n")

        # HW 2: Verify that register works (re-register for next part)
        reg_response = self.server.RegisterVoter(eVoting_pb2.Voter(name="Vidar", group="Group A", public_key=verify_key_bytes))
        if reg_response.code == 0:
            with open("private_key_vidar", "wb") as f:
                f.write(sign_key.encode()) 
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------Re-reg done(0)-------------\n")

        sign_key = SigningKey.generate()
        # with open("private_key_alice", "wb") as f:
        #     f.write(sign_key.encode())
        verify_key = sign_key.verify_key
        verify_key_bytes = verify_key.encode()
        
        # Voter 2: Alice
        # HW 2: Verify that register works (register)
        reg_response = self.server.RegisterVoter(eVoting_pb2.Voter(name="Alice", group="Group A", public_key=verify_key_bytes))
        if reg_response.code == 0:
            with open("private_key_alice", "wb") as f:
                f.write(sign_key.encode()) 
        print("Voter list:")
        self.server.get_registers_name_list()
        # print(self.server.registration_table)
        print("-------------Reg done(0)-------------\n")


    # HW2: RPC call
    def PreAuth(self, request, context):
        voter_name = request
        key = voter_name.name
        challenge = secrets.token_bytes(4) # challenge_size = 4
        print(f"1. Received PreAuth. Voter: {key}")
        # self.server.challenge_table[key] = challenge # add challenge
        self.server.add_challenge(key, challenge)
        print("-------------PreAuth done-------------\n")
        return eVoting_pb2.Challenge(value = bytes(challenge))

    def Auth(self, request, context):
        # print(f'Name: {request.name.name}')
        # print(f'Response: {request.response.value.decode()}\n')

        auth_req = request
        index = auth_req.name.name
        print(f"2. Received Auth. Name: {index}")
        # challenge = self.server.challenge_table[index] # get index
        # public_key = self.server.registration_table[index]["public_key"] # get index's public key
        public_key = self.server.get_register_publicKey(index)
        challenge = self.server.get_challenge(index)

        signature = auth_req.response.value

        # try:
        public_key.verify(smessage=challenge, signature = signature)
        # except:
        #     return eVoting_pb2.AuthToken(value = bytes("invalid", encoding="utf-8"))

        token = secrets.token_bytes(4)  # token size = 4
        expired_time = datetime.now()+timedelta(hours=1)
        # self.server.token_table[token] = {"expired": expired, "name": index}
        self.server.add_token(token, index, expired_time)
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
            # if request.token.value not in self.server.token_table:
            #     return eVoting_pb2.Status(code = 1)
            # if datetime.now() >= self.server.token_table[request.token.value]["expired"]:
            #     return eVoting_pb2.Status(code = 1)
            if  not self.server.is_Valid_token(request.token.value):
                return eVoting_pb2.Status(code = 1)
            
            
            # Status.code=2 : Missing groups or choices specification 
            if len(request.choices) == 0 or len(request.groups) == 0:
                return eVoting_pb2.Status(code = 2)

            # if request.name in self.server.election_table:
            #     return eVoting_pb2.Status(code = 4)
            
            # Status.code=0 : Election created successfully
            self.server.add_election(request)
            # votes = {}
            # for c in request.choices:
            #     votes[c] = 0
            # self.server.election_table[request.name] = {
            #     "end_date" : request.end_date.ToDatetime(),\
            #     "groups" : request.groups,\
            #     "votes" : votes,\
            #     "voters" : []}
            return eVoting_pb2.Status(code = 0) 

        # Status.code=3 : Unknown error
        except:
            return eVoting_pb2.Status(code = 3)
        

    def CastVote(self, request, context):
        election_name = request.election_name
        choice = request.choice_name
        token = request.token.value

        print("Received CastVote.")
        print(f'Election Name: {election_name}')
        print(f'Choice Name: {choice}')
        print(f'Token: {token}\n')

        try: 
            # Status.code=1 : Invalid authentication token
            # if request.token.value not in self.server.token_table:
            #     return eVoting_pb2.Status(code = 1)
            # if datetime.now() >= self.server.token_table[request.token.value]["expired"]:
            #     return eVoting_pb2.Status(code = 1)
            if  not self.server.is_Valid_token(request.token.value):
                return eVoting_pb2.Status(code = 1)
            
            # Status.code=2 : Invalid election name
            # if request.election_name not in self.server.election_table:
            #     return eVoting_pb2.Status(code = 2)
            # if datetime.now() > self.server.election_table[request.election_name]["end_date"]:
            #     return eVoting_pb2.Status(code = 2)
            if not self.server.existed_election(request.election_name):
                return eVoting_pb2.Status(code = 2)
            if self.server.isDue_election(request.election_name):
                return eVoting_pb2.Status(code = 2)
            
            # Status.code=3 : The voter’s group is not allowed in the election
            # name = self.server.token_table[request.token.value]["name"]
            # group = self.server.registration_table[name]["group"]
            voter_name = self.server.get_voter_name(token)
            group = self.server.get_voter_group(voter_name)
            # if group not in self.server.election_table[request.election_name]["groups"]:
            if not self.server.valid_group(election_name, group):
                return eVoting_pb2.Status(code = 3)
            
            # Status.code=4 : A previous vote has been cast.
            # if name in self.server.election_table[request.election_name]["voters"]:
            if self.server.repeated_vote(election_name, voter_name):
                return eVoting_pb2.Status(code = 4)
               
            # Status.code=0 : Successful vote
            # self.server.election_table[request.election_name]["votes"][request.choice_name] += 1
            # self.server.election_table[request.election_name]["voters"].append(name)
            self.server.add_vote(election_name, choice, voter_name)
            return eVoting_pb2.Status(code = 0)
        
        # Status.code=5 : Unknown error
        except:
            return eVoting_pb2.Status(code = 5)


    def GetResult(self, request, context):
        index = request.name
        print("Received GetResult.")
        print(f'Election Name: {index}\n')

        result = eVoting_pb2.ElectionResult()
        
        # ElectionResult.status = 1: Non-existent election
        # if request.name not in self.server.election_table:
        if not self.server.existed_election(index):
            result.status = 1
            return result
        
        # ElectionResult.status = 2: The election is still ongoing. Election result is not available yet
        # if datetime.now() > self.server.election_table[request.name]["end_date"]:
        if self.server.due_election(index):
            result.status = 2
            return result
        
        # query is successful: ElectionReuslt.status = 0
        result.status = 0

        for choice, ballot in self.server.get_result(index).items():
            curVoteCount = result.counts.add()
            curVoteCount.choice_name = choice
            curVoteCount.count = ballot

        return result 
    
    
    
def serve(grpc_port, db_port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    eVoting_pb2_grpc.add_eVotingServicer_to_server(
        eVotingServicer(db_port), server)
    server.add_insecure_port('[::]:' + grpc_port) 
    server.start()
    print("Server started, listening on " + grpc_port, end='\n\n')
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print('PLease input grpc serverand db server ports')
        sys.exit()
    
    logging.basicConfig()
    serve(sys.argv[1], sys.argv[2])