import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hemerapp/models/bot_model.dart';

class ChatRoute extends StatefulWidget {
  const ChatRoute({super.key});

  @override
  ChatRouteState createState() => ChatRouteState();
}

class ChatRouteState extends State<ChatRoute> {
  late BotModel bot;
  late Future<String> token;
  late String username;
  final FlutterSecureStorage storage = const FlutterSecureStorage();
  @override
  void initState() {
    super.initState();
  }

  @override
  Future<void> didChangeDependencies() async {
    super.didChangeDependencies();
    bot = ModalRoute.of(context)!.settings.arguments as BotModel;
    token = _getToken();
    username = (await storage.read(key: 'username'))!;
  }

  Future<String> _getToken() async {
    String? value = "";
    if(bot.isPryvRequired) {
      value = await storage.read(key: bot.name);
    }
    return value!;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: FutureBuilder<String>(
                  future: token,
                  builder: (context, snapshot) {
                    if (snapshot.hasData) {
                      return Text(snapshot.data! + bot.name +username);
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
