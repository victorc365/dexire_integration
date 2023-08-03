// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'authentication_response_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuthenticationResponseModel _$AuthenticationResponseModelFromJson(Map<String, dynamic> json) =>
    AuthenticationResponseModel(
      json['status'] as String,
      json['authUrl'] as String,
      json['key'] as String,
      json['poll'] as String,
    );

Map<String, dynamic> _$AuthenticationResponseModelToJson(AuthenticationResponseModel instance) =>
    <String, dynamic>{
      'status': instance.status,
      'authUrl': instance.authUrl,
      'key': instance.key,
      'poll': instance.poll,
    };
