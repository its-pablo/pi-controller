# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: messages.proto
# Protobuf Python Version: 5.27.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    27,
    2,
    '',
    'messages.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0emessages.proto\x12\x08messages\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/duration.proto\"\xb4\x08\n\tcontainer\x12\x13\n\theartbeat\x18\x01 \x01(\x05H\x00\x12\x35\n\tset_state\x18\x02 \x01(\x0b\x32 .messages.container.DEVICE_STATEH\x00\x12\x14\n\nget_states\x18\x03 \x01(\x05H\x00\x12\x33\n\x06states\x18\x04 \x01(\x0b\x32!.messages.container.DEVICE_STATESH\x00\x12?\n\tset_event\x18\x05 \x01(\x0b\x32*.messages.container.SCHEDULED_DEVICE_EVENTH\x00\x12\x14\n\nget_events\x18\x06 \x01(\tH\x00\x12\x18\n\x0eget_all_events\x18\x07 \x01(\x05H\x00\x12=\n\x06\x65vents\x18\x08 \x01(\x0b\x32+.messages.container.SCHEDULED_DEVICE_EVENTSH\x00\x12\x13\n\tno_events\x18\t \x01(\tH\x00\x12\x42\n\x0c\x63\x61ncel_event\x18\n \x01(\x0b\x32*.messages.container.SCHEDULED_DEVICE_EVENTH\x00\x12\x13\n\tpeak_logs\x18\x0b \x01(\x05H\x00\x12\x0e\n\x04logs\x18\x0c \x01(\tH\x00\x12\x0e\n\x04info\x18\r \x01(\tH\x00\x12\x10\n\x06pubkey\x18\x0e \x01(\x0cH\x00\x12\x12\n\x08password\x18\x0f \x01(\x0cH\x00\x12\x0e\n\x04\x61uth\x18\x10 \x01(\x08H\x00\x12\x39\n\rdemo_override\x18\x62 \x01(\x0b\x32 .messages.container.DEVICE_STATEH\x00\x12\x12\n\x08shutdown\x18\x63 \x01(\x05H\x00\x1aV\n\x0c\x44\x45VICE_STATE\x12\x13\n\x0b\x64\x65vice_name\x18\x01 \x01(\t\x12\x1e\n\x05state\x18\x02 \x01(\x0e\x32\x0f.messages.STATE\x12\x11\n\tis_output\x18\x03 \x01(\x08\x1a@\n\rDEVICE_STATES\x12/\n\x05state\x18\x01 \x03(\x0b\x32 .messages.container.DEVICE_STATE\x1a\xd0\x01\n\x16SCHEDULED_DEVICE_EVENT\x12-\n\ttimestamp\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12+\n\x08\x64uration\x18\x02 \x01(\x0b\x32\x19.google.protobuf.Duration\x12)\n\x06period\x18\x03 \x01(\x0b\x32\x19.google.protobuf.Duration\x12/\n\x05state\x18\x04 \x01(\x0b\x32 .messages.container.DEVICE_STATE\x1aT\n\x17SCHEDULED_DEVICE_EVENTS\x12\x39\n\x05\x65vent\x18\x01 \x03(\x0b\x32*.messages.container.SCHEDULED_DEVICE_EVENTB\n\n\x08\x63ontents*^\n\x05STATE\x12\x0b\n\x07\x44\x45V_UNK\x10\x00\x12\x0e\n\nDEV_ACTIVE\x10\x01\x12\x10\n\x0c\x44\x45V_INACTIVE\x10\x02\x12\x13\n\x0f\x44\x45V_UNINHIBITED\x10\x03\x12\x11\n\rDEV_INHIBITED\x10\x04\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'messages_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STATE']._serialized_start=1172
  _globals['_STATE']._serialized_end=1266
  _globals['_CONTAINER']._serialized_start=94
  _globals['_CONTAINER']._serialized_end=1170
  _globals['_CONTAINER_DEVICE_STATE']._serialized_start=709
  _globals['_CONTAINER_DEVICE_STATE']._serialized_end=795
  _globals['_CONTAINER_DEVICE_STATES']._serialized_start=797
  _globals['_CONTAINER_DEVICE_STATES']._serialized_end=861
  _globals['_CONTAINER_SCHEDULED_DEVICE_EVENT']._serialized_start=864
  _globals['_CONTAINER_SCHEDULED_DEVICE_EVENT']._serialized_end=1072
  _globals['_CONTAINER_SCHEDULED_DEVICE_EVENTS']._serialized_start=1074
  _globals['_CONTAINER_SCHEDULED_DEVICE_EVENTS']._serialized_end=1158
# @@protoc_insertion_point(module_scope)
