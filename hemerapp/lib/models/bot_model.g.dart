// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bot_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BotModel _$BotModelFromJson(Map<String, dynamic> json) => BotModel(
      json['name'] as String,
      json['description'] as String,
      json['icon'] as String?,
      json['url'] as String,
      json['isDev'] as bool? ?? false,
      json['isPryvRequired'] as bool,
      (json['requiredPermissions'] as List<dynamic>)
          .map((e) =>
              RequestedPermissionModel.fromJson(e as Map<String, dynamic>))
          .toList(),
    );

Map<String, dynamic> _$BotModelToJson(BotModel instance) => <String, dynamic>{
      'name': instance.name,
      'description': instance.description,
      'icon': instance.icon,
      'url': instance.url,
      'isDev': instance.isDev,
      'isPryvRequired': instance.isPryvRequired,
      'requiredPermissions': instance.requiredPermissions,
    };
