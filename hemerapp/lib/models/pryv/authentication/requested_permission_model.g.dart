// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'requested_permission_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

RequestedPermissionModel _$RequestedPermissionModelFromJson(Map<String, dynamic> json) =>
    RequestedPermissionModel(
      json['streamId'] as String,
      json['level'] as String,
      json['defaultName'] as String,
    );

Map<String, dynamic> _$RequestedPermissionModelToJson(RequestedPermissionModel instance) =>
    <String, dynamic>{
      'streamId': instance.streamId,
      'level': instance.level,
      'defaultName': instance.defaultName,
    };
