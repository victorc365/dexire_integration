import 'package:json_annotation/json_annotation.dart';

part 'service_info_model.g.dart';

@JsonSerializable()
class ServiceInfoModel {
  ServiceInfoModel(this.version, this.serial,this.register, this.access, this.api, this.name, this.home, this.support, this.terms, this.eventTypes);

  String serial;
  String register;
  String access;
  String api;
  String name;
  String home;
  String support;
  String terms;
  String eventTypes;
  String version;

  factory ServiceInfoModel.fromJson(Map<String, dynamic> json) =>
      _$ServiceInfoModelFromJson(json);

  Map<String, dynamic> toJson() => _$ServiceInfoModelToJson(this);
}
