// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'bot_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BotModel _$BotModelFromJson(Map<String, dynamic> json) =>
    BotModel(
      json['name'] as String,
      json['icon'] as String?,
      json['url'] as String,
      json['isDev'] as bool? ?? false,
    );

Map<String, dynamic> _$BotModelToJson(BotModel instance) =>
    <String, dynamic>{
      'name': instance.name,
      'icon': instance.icon,
      'url': instance.url,
      'isDev': instance.isDev,
    };
