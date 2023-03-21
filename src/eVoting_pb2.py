# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: eVoting.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\reVoting.proto\x12\x06voting\x1a\x1fgoogle/protobuf/timestamp.proto\"8\n\x05Voter\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\r\n\x05group\x18\x02 \x02(\t\x12\x12\n\npublic_key\x18\x03 \x02(\x0c\"\x19\n\tVoterName\x12\x0c\n\x04name\x18\x01 \x02(\t\"\x16\n\x06Status\x12\x0c\n\x04\x63ode\x18\x01 \x02(\x05\"\x1a\n\tChallenge\x12\r\n\x05value\x18\x01 \x02(\x0c\"\x19\n\x08Response\x12\r\n\x05value\x18\x01 \x02(\x0c\"R\n\x0b\x41uthRequest\x12\x1f\n\x04name\x18\x01 \x02(\x0b\x32\x11.voting.VoterName\x12\"\n\x08response\x18\x02 \x02(\x0b\x32\x10.voting.Response\"\x1a\n\tAuthToken\x12\r\n\x05value\x18\x01 \x02(\x0c\"\x89\x01\n\x08\x45lection\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x0e\n\x06groups\x18\x02 \x03(\t\x12\x0f\n\x07\x63hoices\x18\x03 \x03(\t\x12,\n\x08\x65nd_date\x18\x04 \x02(\x0b\x32\x1a.google.protobuf.Timestamp\x12 \n\x05token\x18\x05 \x02(\x0b\x32\x11.voting.AuthToken\"T\n\x04Vote\x12\x15\n\relection_name\x18\x01 \x02(\t\x12\x13\n\x0b\x63hoice_name\x18\x02 \x02(\t\x12 \n\x05token\x18\x03 \x02(\x0b\x32\x11.voting.AuthToken\"\x1c\n\x0c\x45lectionName\x12\x0c\n\x04name\x18\x01 \x02(\t\"/\n\tVoteCount\x12\x13\n\x0b\x63hoice_name\x18\x01 \x02(\t\x12\r\n\x05\x63ount\x18\x02 \x02(\x05\"C\n\x0e\x45lectionResult\x12\x0e\n\x06status\x18\x01 \x02(\x05\x12!\n\x06\x63ounts\x18\x02 \x03(\x0b\x32\x11.voting.VoteCount2\x83\x02\n\x07\x65Voting\x12/\n\x07PreAuth\x12\x11.voting.VoterName\x1a\x11.voting.Challenge\x12.\n\x04\x41uth\x12\x13.voting.AuthRequest\x1a\x11.voting.AuthToken\x12\x32\n\x0e\x43reateElection\x12\x10.voting.Election\x1a\x0e.voting.Status\x12(\n\x08\x43\x61stVote\x12\x0c.voting.Vote\x1a\x0e.voting.Status\x12\x39\n\tGetResult\x12\x14.voting.ElectionName\x1a\x16.voting.ElectionResult')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'eVoting_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VOTER._serialized_start=58
  _VOTER._serialized_end=114
  _VOTERNAME._serialized_start=116
  _VOTERNAME._serialized_end=141
  _STATUS._serialized_start=143
  _STATUS._serialized_end=165
  _CHALLENGE._serialized_start=167
  _CHALLENGE._serialized_end=193
  _RESPONSE._serialized_start=195
  _RESPONSE._serialized_end=220
  _AUTHREQUEST._serialized_start=222
  _AUTHREQUEST._serialized_end=304
  _AUTHTOKEN._serialized_start=306
  _AUTHTOKEN._serialized_end=332
  _ELECTION._serialized_start=335
  _ELECTION._serialized_end=472
  _VOTE._serialized_start=474
  _VOTE._serialized_end=558
  _ELECTIONNAME._serialized_start=560
  _ELECTIONNAME._serialized_end=588
  _VOTECOUNT._serialized_start=590
  _VOTECOUNT._serialized_end=637
  _ELECTIONRESULT._serialized_start=639
  _ELECTIONRESULT._serialized_end=706
  _EVOTING._serialized_start=709
  _EVOTING._serialized_end=968
# @@protoc_insertion_point(module_scope)