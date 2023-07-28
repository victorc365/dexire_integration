import 'package:json_annotation/json_annotation.dart';

part 'bot_model.g.dart';

@JsonSerializable()
class BotModel {
  BotModel(this.name, this.icon, this.url, this.isDev);

  String name;
  String? icon;
  String url;

  @JsonKey(defaultValue: false)
  bool isDev;

  factory BotModel.fromJson(Map<String, dynamic> json) =>
      _$BotModelFromJson(json);

  Map<String, dynamic> toJson() => _$BotModelToJson(this);
}
