import 'package:json_annotation/json_annotation.dart';

part 'requested_permission_model.g.dart';

@JsonSerializable()
class RequestedPermissionModel {
  RequestedPermissionModel(this.streamId, this.level, this.defaultName);

  String streamId;
  String level;
  String defaultName;

  factory RequestedPermissionModel.fromJson(Map<String, dynamic> json) =>
      _$RequestedPermissionModelFromJson(json);

  Map<String, dynamic> toJson() => _$RequestedPermissionModelToJson(this);
}
