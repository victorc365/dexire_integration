import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';

class ChatRoute extends StatefulWidget {
  const ChatRoute({super.key});

  @override
  ChatRouteState createState() => ChatRouteState();
}

class ChatRouteState extends State<ChatRoute> {
  late BotModel bot;
  String token = 'undefined';
  late String username;
  bool isConnected = false;

  final FlutterSecureStorage storage = const FlutterSecureStorage();
  @override
  void initState() {
    super.initState();
  }

  @override
  Future<void> didChangeDependencies() async {
    super.didChangeDependencies();
    bot = ModalRoute.of(context)!.settings.arguments as BotModel;
  }

  Future<bool> _connectToBot() async {
    if (bot.isPryvRequired) {
      token = (await storage.read(key: bot.name))!;
      username = (await storage.read(key: 'username'))!;
    } else {
      username = 'Anonymous';

    }

    return await connectToBot(bot.name, username, token);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: FutureBuilder<bool>(
                  future: _connectToBot(),
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      return Text(
                          'bot name:${bot.name}\n$username\ntoken:$token\nconnected:$isConnected');
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
}
