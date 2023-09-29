import 'package:hemerapp/models/pryv/authentication/requested_permission_model.dart';
import 'package:json_annotation/json_annotation.dart';

part 'bot_model.g.dart';

enum BotStatus { running }

@JsonSerializable()
class BotModel {
  BotModel(this.name, this.description,this.icon, this.url, this.isDev, this.isPryvRequired,
      this.requiredPermissions);

  String name;
  String description;
  String? icon;
  String url;
  bool isPryvRequired;
  List<RequestedPermissionModel> requiredPermissions;
  @JsonKey(defaultValue: false)
  bool isDev;

  factory BotModel.fromJson(Map<String, dynamic> json) =>
      _$BotModelFromJson(json);

  Map<String, dynamic> toJson() => _$BotModelToJson(this);
}
