from concurrent import futures
import logging
import signal
import sys

import grpc

import eVoting_pb2
import eVoting_pb2_grpc

from datetime import datetime

def RegisterVoter(voter: eVoting_pb2.Voter) -> eVoting_pb2.Status:
    pass

def UnregisterVoter(votername: eVoting_pb2.VoterName) -> eVoting_pb2.Status:
    pass

class eVotingServicer(eVoting_pb2_grpc.eVotingServicer):
    def PreAuth(self, request, context):
        print("Received PreAuth.")
        print(f'Name: {request.name}\n')
        return eVoting_pb2.Challenge(value = '1'.encode())

    def Auth(self, request, context):
        print("Received Auth.")
        print(f'Name: {request.name.name}')
        print(f'Response: {request.response.value.decode()}\n')
        return eVoting_pb2.AuthToken(value = '2'.encode())

    def CreateElection(self, request, context):
        print("Received CreateElection.")
        print(f'Name: {request.name}')
        print(f'Groups: {request.groups[0]}')
        print(f'Choices: {request.choices[0]}')
        print(f'Time: {datetime.fromtimestamp(request.end_date.seconds)}')
        print(f'Token: {request.token.value.decode()}\n')
        return eVoting_pb2.Status(code = 3)

    def CastVote(self, request, context):
        print("Received CastVote.")
        print(f'Election Name: {request.election_name}')
        print(f'Choice Name: {request.choice_name}')
        print(f'Token: {request.token.value.decode()}\n')
        return eVoting_pb2.Status(code = 4)

    def GetResult(self, request, context):
        print("Received GetResult.")
        print(f'Election Name: {request.name}\n')

        result = eVoting_pb2.ElectionResult()
        result.status = 5

        curVoteCount = result.counts.add()
        curVoteCount.choice_name = 'Bob'
        curVoteCount.count = 50

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