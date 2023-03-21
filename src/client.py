from __future__ import print_function

import logging

import grpc

import eVoting_pb2
import eVoting_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

def run():
    port = '34652'
    channel = grpc.insecure_channel('localhost:' + port)
    stub = eVoting_pb2_grpc.eVotingStub(channel)

    response = stub.PreAuth(eVoting_pb2.VoterName(name = 'Alice'))
    print('Response message of PreAuth.')
    print(f'Challenge: {response.value.decode()}\n')

    response = stub.Auth(eVoting_pb2.AuthRequest(name = eVoting_pb2.VoterName(name = 'Alice'), \
                                                 response = eVoting_pb2.Response(value = '1'.encode())))
    print('Response message of Auth')
    print(f'AuthToken: {response.value.decode()}\n')

    curElection = eVoting_pb2.Election()
    curElection.name = 'Election A'
    curElection.groups.append('Group A')    #extend
    curElection.choices.append('Bob')
    curElection.end_date.GetCurrentTime()
    curElection.token.value = '2'.encode()
    response = stub.CreateElection(curElection)
    print('Response message of CreateElection')
    print(f'Status: {response.code}\n')

    response = stub.CastVote(eVoting_pb2.Vote(election_name = 'Election A', \
                                                   choice_name = 'Bob', \
                                                    token = eVoting_pb2.AuthToken(value = '3'.encode())))
    print('Response message of CastVote')
    print(f'Status: {response.code}\n')

    response = stub.GetResult(eVoting_pb2.ElectionName(name = 'Election A'))
    print('Response message of CastVote')
    print(f'Status: {response.status}')
    print(f'VoteCount: {response.counts[0].choice_name}, {response.counts[0].count}')


if __name__ == '__main__':
    logging.basicConfig()
    run()
