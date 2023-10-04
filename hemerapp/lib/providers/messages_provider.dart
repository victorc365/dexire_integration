import 'dart:async';
import 'dart:convert';
import 'dart:developer' as developer;

import 'package:flutter/material.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/models/message_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:developer' as developer;

class MessagesProvider with ChangeNotifier {
  final _repository = BotsRepository();
  final String target = 'hemerapp';
  String currentContext = 'contextual';
  bool isLoading = false;
  bool _isConnected = false;
  List<MessageModel> _messages = [];

  List<MessageModel> get messages => _messages;

  WebSocketChannel? channel;

  Future<void> openChannel(username, botName, token) async {
    _isConnected = false;
    _messages = [];
    isLoading = true;
    if (channel != null) {
      channel?.sink.close();
      channel = null;
    }
    notifyListeners();

    if (!_isConnected) {
      await _repository.connectToBot(botName, username, token);
    }

    Timer.periodic(const Duration(seconds: 2), (timer) async {
      if (!_isConnected) {
        String status = await _repository.getStatus("${botName}_$username");
        if (status.toLowerCase() == BotStatus.running.name) {
          _isConnected = true;
          if (_isConnected && channel == null) {
            while (channel == null) {
              try {
                channel = _repository.openWebsocketChannel(username, botName);
                channel?.stream.listen((event) {
                  MessageModel messageModel =
                      MessageModel.fromJson(jsonDecode(event));
                  developer.log(messageModel.body!);
                  _messages.add(messageModel);
                  currentContext = messageModel.metadata?['context'];
                  notifyListeners();
                });
              } on Exception {
                continue;
              }
            }
          }
        }
      } else {
        timer.cancel();
        isLoading = false;
        notifyListeners();
      }
    });
  }

  Future<void> sendMessage(MessageModel message) async {
    message.metadata ??= {};
    message.metadata?['context'] = currentContext;
    message.metadata?['target'] = target;
    _messages.add(message);
    channel!.sink.add(jsonEncode(message));
    currentContext = 'contextual';
    notifyListeners();
  }
}
