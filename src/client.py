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

# HW 3: Client try to send request to primary, if timeout occurs, send request to backup node
def try_primary(primary_rpc, backup_rpc, request):
    try:
        response = primary_rpc(request, timeout=30)
        print('-----Get response from primary node-----')
    except:
        response = backup_rpc(request, timeout=30)
        print('-----Get response from backup node-----')
    return response

# HW 3: Client build connection to both primary and backup node
def connect(primary_ip, primary_port, backup_ip, backup_port):
    channel = grpc.insecure_channel(primary_ip + ':' + primary_port)
    primary_stub = eVoting_pb2_grpc.eVotingStub(channel)

    channel = grpc.insecure_channel(backup_ip + ':' + backup_port)
    backup_stub = eVoting_pb2_grpc.eVotingStub(channel)

    return primary_stub, backup_stub

def run(primary_stub, backup_stub):
    # HW2: Reading private key 
    with open("private_key_vidar", "rb") as f:
        Vidar_key= f.read()
    with open("private_key_alice", "rb") as f:
        Alice_key= f.read()

    sign_key_list = []
    sign_key_list.append(SigningKey(Vidar_key))
    sign_key_list.append(SigningKey(Alice_key))
    voter_list = ['Vidar', 'Alice']

    """
    Use voter 'Vidar' to create election initially
    """
    print('Use first voter to create election initially')
    # HW2: PreAuth
    pre_response = try_primary(primary_stub.PreAuth, backup_stub.PreAuth, \
        eVoting_pb2.VoterName(name = voter_list[0]))

    print('Response message of PreAuth.')
    print(f'PreAuth: {pre_response.value}\n')

    # HW2: Auth
    challenge = pre_response.value
    signed = sign_key_list[0].sign(challenge)
    signature = signed.signature

    auth_response = try_primary(primary_stub.Auth, backup_stub.Auth,
        eVoting_pb2.AuthRequest(
            name = eVoting_pb2.VoterName(name = voter_list[0]),\
            response = eVoting_pb2.Response(value = bytes(signature))\
    ))
    token = auth_response.value

    print('Response message of Auth.')
    print(f'Auth: {auth_response.value}\n')

    # election config 
    election_name = 'What color do you like'
    groups = ["Group A", "Group B"]
    choices = ["Red", "Blue", "White", "Yellow"]
    due = datetime.now() + timedelta(seconds=40)

    curElection = eVoting_pb2.Election()
    curElection.name = election_name
    curElection.groups.extend(groups)
    curElection.choices.extend(choices)
    curElection.end_date.FromDatetime(due)
    curElection.token.value = bytes(token)
    
    create_election_response = try_primary(primary_stub.CreateElection, \
        backup_stub.CreateElection, curElection)
    print('Response message of CreateElection')
    print(f'Status: {create_election_response.code}')

    print("Create Election:")
    print(f'Name: {election_name}')
    print(f'Groups: {groups}')
    print(f'Choices: {choices}')
    print(f'Due Time: {due}')

    for i in range(2):
        # HW2: PreAuth
        voter_id = int(input('\nInput your voter id (0: Viadr, 1: Alice)\n'))
        while voter_id != 0 and voter_id != 1:
            print('Invalid voter id!')
            voter_id = int(input('\nInput voter id (0: Viadr, 1: Alice)\n'))
        pre_response = try_primary(primary_stub.PreAuth, backup_stub.PreAuth, \
            eVoting_pb2.VoterName(name = voter_list[voter_id]))
        
        print('Response message of PreAuth.')
        print(f'PreAuth: {pre_response.value}\n')

        # HW2: Auth
        challenge = pre_response.value
        signed = sign_key_list[voter_id].sign(challenge)
        signature = signed.signature

        auth_response = try_primary(primary_stub.Auth, backup_stub.Auth,
            eVoting_pb2.AuthRequest(
                name = eVoting_pb2.VoterName(name = voter_list[voter_id]),\
                response = eVoting_pb2.Response(value = bytes(signature))\
        ))
        token = auth_response.value

        print('Response message of Auth.')
        print(f'Auth: {auth_response.value}\n')
        
        # call castvote
        r = int(input("What color do you like? (0: red, 1: blue, 2: white, 3: yellow)\n"))
        while r < 0 or r > 3:
            print('Invalid choice!')
            r = int(input("\nWhat color do you like? (0: red, 1: blue, 2: white, 3: yellow)\n"))
        castvote_response = try_primary(primary_stub.CastVote, backup_stub.CastVote, \
            eVoting_pb2.Vote(election_name = election_name, \
                            choice_name = choices[r], \
                            token = eVoting_pb2.AuthToken(value = bytes(token))))
        
        print('Response message of CastVote')
        print(f'Status: {castvote_response.code}\n')
        
        # call getresult
        get_result_response = try_primary(primary_stub.GetResult, backup_stub.GetResult, \
            eVoting_pb2.ElectionName(name = election_name))
        print('Response message of GetResult ')
        print(f'Status: {get_result_response.status}\n')

        # result
        for votecnt in get_result_response.counts:
            print("Choice {} got {} ballots in election!".format(votecnt.choice_name, votecnt.count))
    
    # Call getresult after the election ended
    cur_time = datetime.now()
    while((cur_time - timedelta(seconds=1)) < due):
        remainig_time = int((due - cur_time).total_seconds())
        print(f'The electoin will end in {remainig_time} seconds.')
        sleep(1)
        cur_time = datetime.now()
    
    # call getresult
    get_result_response = try_primary(primary_stub.GetResult, backup_stub.GetResult, \
        eVoting_pb2.ElectionName(name = election_name))
    print('Response message of GetResult ')
    print(f'Status: {get_result_response.status}\n')

    print('The election result is:')
    # result
    for votecnt in get_result_response.counts:
        print("Choice {} got {} ballots in election!".format(votecnt.choice_name, votecnt.count))

if __name__ == '__main__':
    logging.basicConfig()
    primary_stub, backup_stub = connect('localhost', '55555', 'localhost', '55556')
    run(primary_stub, backup_stub)
