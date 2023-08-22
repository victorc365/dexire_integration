import 'package:json_annotation/json_annotation.dart';

part 'authentication_response_model.g.dart';

@JsonSerializable()
class AuthenticationResponseModel {
  AuthenticationResponseModel(this.status, this.authUrl, this.key, this.poll);

  String status;
  String authUrl;
  String key;
  String poll;

  factory AuthenticationResponseModel.fromJson(Map<String, dynamic> json) =>
      _$AuthenticationResponseModelFromJson(json);

  Map<String, dynamic> toJson() => _$AuthenticationResponseModelToJson(this);
}
