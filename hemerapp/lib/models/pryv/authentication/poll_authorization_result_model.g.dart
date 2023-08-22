// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'poll_authorization_result_model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PollAuthorizationResultModel _$PollAuthorizationResultModelFromJson(Map<String, dynamic> json) =>
    PollAuthorizationResultModel(
      json['status'] as String,
      json['apiEndpoint'] as String?,

    );

Map<String, dynamic> _$PollAuthorizationResultModelToJson(PollAuthorizationResultModel instance) =>
    <String, dynamic>{
      'status': instance.status,
      'apiEndpoint': instance.apiEndpoint,


    };
