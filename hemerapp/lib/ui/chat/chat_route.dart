
import 'package:flutter/material.dart';

class ChatRoute extends StatefulWidget {
  const ChatRoute({super.key});

  @override
  ChatRouteState createState() => ChatRouteState();
}

class ChatRouteState extends State<ChatRoute> {
  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
                child: Text('Chat route'))
          ],
        ),
      ),
    );
  }
}