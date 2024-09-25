import 'package:flutter/material.dart';

class TextMessage extends StatelessWidget {
  const TextMessage({super.key, required this.text, required this.isUser});

  final String text;
  final bool isUser;

  //TODO: Add enrich text features
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(left: 14, right: 14, top: 10, bottom: 10),
      child: Align(
        alignment: isUser ? Alignment.topLeft : Alignment.topRight,
        child: Container(
          decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: isUser ? Colors.grey.shade200 : Colors.blue[200]),
          padding: const EdgeInsets.all(16),
          child: Text(
            text,
            style: const TextStyle(fontSize: 15),
          ),
        ),
      ),
    );
  }
}
