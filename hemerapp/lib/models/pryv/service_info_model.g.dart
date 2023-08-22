// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'service_info_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ServiceInfoModel _$ServiceInfoModelFromJson(Map<String, dynamic> json) =>
    ServiceInfoModel(
      json['serial'] as String,
      json['version'] as String,
      json['register'] as String,
      json['access'] as String,
      json['api'] as String,
      json['name'] as String,
      json['home'] as String,
      json['support'] as String,
      json['terms'] as String,
      json['eventTypes'] as String,
    );

Map<String, dynamic> _$ServiceInfoModelToJson(ServiceInfoModel instance) =>
    <String, dynamic>{
      'serial': instance.serial,
      'register': instance.register,
      'access': instance.access,
      'api': instance.api,
      'name': instance.name,
      'home': instance.home,
      'support': instance.support,
      'terms': instance.terms,
      'eventTypes': instance.eventTypes,
      'version': instance.version
    };
