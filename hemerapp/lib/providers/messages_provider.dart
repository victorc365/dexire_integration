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
  Map<String, dynamic>? botKeyboard;

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
                  String context = messageModel.metadata?['context'];

                  switch (context) {
                    case 'history':
                      currentContext = 'contextual';
                      List<dynamic> jsonHistory =
                          jsonDecode(messageModel.body!);
                      List<MessageModel> history = [];
                      for (var hist in jsonHistory) {
                        var m = MessageModel(hist['to'], hist['sender'],
                            hist['body'], null, hist['metadata']);
                        history.add(m);
                      }
                      _messages.insertAll(0, history);
                      break;
                    case 'keyboard':
                      botKeyboard = jsonDecode(messageModel.body!);
                      break;
                    default:
                      _messages.add(messageModel);
                      currentContext = context;
                      break;
                  }

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
    message.metadata?['body_format'] = 'text';
    _messages.add(message);
    channel!.sink.add(jsonEncode(message));
    currentContext = 'contextual';
    notifyListeners();
  }

  Future<void> sendInternalMessage(MessageModel message) async {
    message.metadata ??= {};
    message.metadata?['context'] = currentContext;
    message.metadata?['target'] = target;
    channel!.sink.add(jsonEncode(message));
    currentContext = 'contextual';
    notifyListeners();
  }
}
