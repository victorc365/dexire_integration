import 'package:flutter/material.dart';

class BotKeyboard extends StatefulWidget {
  const BotKeyboard({super.key, required this.items, this.type});

  final List<dynamic>? items;
  final String? type;

  @override
  State<BotKeyboard> createState() => _BotKeyboardState();

  
}

class _BotKeyboardState extends State<BotKeyboard> {


  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    throw UnimplementedError();
  }

}

