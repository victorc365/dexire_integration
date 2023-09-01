import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';
import 'package:flutter_chat_types/flutter_chat_types.dart' as types;
import 'package:flutter_chat_ui/flutter_chat_ui.dart';
import 'package:uuid/uuid.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class ChatRoute extends StatefulWidget {
  const ChatRoute({super.key});

  @override
  ChatRouteState createState() => ChatRouteState();
}

class ChatRouteState extends State<ChatRoute> {
  final Uuid uuid = const Uuid();
  String token = 'undefined';
  bool isConnected = false;
  final List<types.Message> _messages = [];
  WebSocketChannel? channel;
  late BotModel bot;
  late String username;
  late types.User _user;

  final FlutterSecureStorage storage = const FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
  }

  Future<bool> _connectToBot() async {
    bot = ModalRoute.of(context)!.settings.arguments as BotModel;
    if (bot.isPryvRequired) {
      token = (await storage.read(key: bot.name))!;
      username = (await storage.read(key: 'username'))!;
    } else {
      username = 'Anonymous';
    }
    _user = types.User(id: username);
    await connectToBot(bot.name, username, token);
    Timer.periodic(const Duration(seconds: 2), (timer) async {
      if (!isConnected) {
        String status = await getStatus("${bot.name}_$username");
        if (status == 'RUNNING') {
          isConnected = true;
          if (isConnected && channel == null) {
            while (channel == null) {
              try {
                channel = openWebsocketChannel(username, bot.name);
              } on Exception catch (e) {
                continue;
              }
            }
          }
        }
      } else {
        timer.cancel();
      }
    });

    return isConnected;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        bottom: false,
        child: Column(
          children: [
            Expanded(
              child: FutureBuilder<bool>(
                  future: _connectToBot(),
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      return Chat(
                        messages: _messages,
                        onSendPressed: _handleSendPressed,
                        user: _user,
                      );
                    }
                    return const Center(
                      child: CircularProgressIndicator(),
                    );
                  }),
            )
          ],
        ),
      ),
    );
  }

  void _addMessage(types.Message message) {
    print(message);
    setState(() {
      _messages.insert(0, message);
    });
  }

  void _handleSendPressed(types.PartialText message) {
    final textMessage = types.TextMessage(
      author: _user,
      createdAt: DateTime.now().millisecondsSinceEpoch,
      id: uuid.v1(),
      text: message.text,
    );

    _addMessage(textMessage);
    channel!.sink.add(jsonEncode(textMessage.toJson()));
  }
}
