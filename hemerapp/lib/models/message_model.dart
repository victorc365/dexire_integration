import 'package:json_annotation/json_annotation.dart';

part 'message_model.g.dart';

@JsonSerializable()
class MessageModel {
  MessageModel(this.to, this.sender, this.body, this.thread, this.metadata);

  String? to;
  String? sender;
  String? body;
  String? thread;
  Map<String, dynamic>? metadata;

  factory MessageModel.fromJson(Map<String, dynamic> json) =>
      _$MessageModelFromJson(json);

  Map<String, dynamic> toJson() => _$MessageModelToJson(this);
}
