// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MessageModel _$MessageModelFromJson(Map<String, dynamic> json) => MessageModel(
      json['to'] as String?,
      json['sender'] as String?,
      json['body'] as dynamic?,
      json['thread'] as String?,
      json['metadata'] as Map<String, dynamic>?,
    );

Map<String, dynamic> _$MessageModelToJson(MessageModel instance) =>
    <String, dynamic>{
      'to': instance.to,
      'sender': instance.sender,
      'body': instance.body,
      'thread': instance.thread,
      'metadata': instance.metadata,
    };
