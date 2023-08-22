import 'package:hemerapp/models/pryv/authentication/requested_permission_model.dart';
import 'package:json_annotation/json_annotation.dart';

part 'authentication_request_model.g.dart';

@JsonSerializable()
class AuthenticationRequestModel {
  AuthenticationRequestModel(this.requestingAppId, this.requestedPermissions);

  String requestingAppId;
  List<RequestedPermissionModel> requestedPermissions;

  factory AuthenticationRequestModel.fromJson(Map<String, dynamic> json) =>
      _$AuthenticationRequestModelFromJson(json);

  Map<String, dynamic> toJson() => _$AuthenticationRequestModelToJson(this);
}
