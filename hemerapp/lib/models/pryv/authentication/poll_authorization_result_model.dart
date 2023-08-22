import 'package:json_annotation/json_annotation.dart';

part 'poll_authorization_result_model.g.dart';

@JsonSerializable()
class PollAuthorizationResultModel {
  PollAuthorizationResultModel(this.status, this.apiEndpoint);

  static const String accepted = "ACCEPTED";
  static const String refused = "REFUSED";
  static const String needSignIn = "NEED_SIGNIN";

  String status;
  String? apiEndpoint;

  factory PollAuthorizationResultModel.fromJson(Map<String, dynamic> json) =>
      _$PollAuthorizationResultModelFromJson(json);

  Map<String, dynamic> toJson() => _$PollAuthorizationResultModelToJson(this);
}

