from __future__ import print_function

import logging
from time import sleep

import grpc
import random

import eVoting_pb2
import eVoting_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

# HW 2
from nacl.signing import SigningKey
from datetime import datetime, timedelta
import base64

def run():
    port = '50051'
    channel = grpc.insecure_channel('localhost:' + port)
    stub = eVoting_pb2_grpc.eVotingStub(channel)

    # HW2: Reading private key 
    with open("private_key", "rb") as f:
        key = f.read()

    # key = base64.b64decode(key)
    sign_key = SigningKey(key)
    
    voter_list = ['Vidar', 'Alice']
    # HW2: PreAuth
    voter_id = int(input('Input your voter id (0: Viadr, 1: Alice)\n'))
    pre_response = stub.PreAuth(eVoting_pb2.VoterName(name = voter_list[voter_id]))

    # HW2: Auth
    challenge = pre_response.value
    signed = sign_key.sign(challenge)
    signature = signed.signature

    auth_response = stub.Auth(eVoting_pb2.AuthRequest(
        name = eVoting_pb2.VoterName(name = voter_list[voter_id]),\
        response = eVoting_pb2.Response(value = bytes(signature))\
    ))

    token = auth_response.value

    # response = stub.PreAuth(eVoting_pb2.VoterName(name = 'Alice'))
    print('Response message of PreAuth.')
    print(f'PreAuth: {pre_response.value}\n')

    print('Response message of Auth.')
    print(f'Auth: {auth_response.value}\n')

    # response = stub.Auth(eVoting_pb2.AuthRequest(name = eVoting_pb2.VoterName(name = 'Alice'), \
    #                                              response = eVoting_pb2.Response(value = '1'.encode())))
    # print('Response message of Auth')
    # print(f'AuthToken: {response.value.decode()}\n')

    # election config 
    election_name = 'what color do you like'
    groups = ["Group A", "Group B"]
    choices = ["Red", "Blue", "White", "Yellow"]
    due = datetime.now() + timedelta(seconds=100)

    curElection = eVoting_pb2.Election()
    curElection.name = election_name
    curElection.groups.extend(groups)
    curElection.choices.extend(choices)
    curElection.end_date.FromDatetime(due)
    curElection.token.value = bytes(token)

    creat_election_response = stub.CreateElection(curElection)
    print('Response message of CreateElection')
    print(f'Status: {creat_election_response.code}\n')

    
    # call castvote
    #r = random.randint(0, 3)
    r = int(input("choice id (0: red, 1: blue, 2: white, 3: yellow)\n"))
    castvote_response = stub.CastVote(eVoting_pb2.Vote(election_name = election_name, \
                                                    choice_name = choices[r], \
                                                    token = eVoting_pb2.AuthToken(value = bytes(token))))
    
    print('Response message of CastVote')
    print(f'Status: {castvote_response.code}\n')
    
    sleep(1)
    # call getresult
    get_result_response = stub.GetResult(eVoting_pb2.ElectionName(name = election_name))
    print('Response message of GetResult ')
    print(f'Status: {get_result_response.status}\n')

    # result
    for votecnt in get_result_response.counts:
        print("Choice {} got {} ballots in election!".format(votecnt.choice_name, votecnt.count))


    


if __name__ == '__main__':
    logging.basicConfig()
    run()
