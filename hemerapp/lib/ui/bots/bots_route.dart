import 'package:flutter/material.dart';

class BotsRoute extends StatelessWidget {
  const BotsRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(child: Text('bots route'))
          ],
        ),
      ),
    );
  }
}