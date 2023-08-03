// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'authentication_request_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuthenticationRequestModel _$AuthenticationRequestModelFromJson(Map<String, dynamic> json) =>
    AuthenticationRequestModel(
      json['requestingAppId'] as String,
      json['requestedPermissions'] as List<RequestedPermissionModel>,
    );

Map<String, dynamic> _$AuthenticationRequestModelToJson(AuthenticationRequestModel instance) =>
    <String, dynamic>{
      'requestingAppId': instance.requestingAppId,
      'requestedPermissions': instance.requestedPermissions,
    };
