import 'package:flutter/material.dart';

class RootRoute extends StatelessWidget {
  final Widget child;
  const RootRoute({super.key, required this.child});

  @override
Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(child: child)
          ],
        ),
      ),
    );
  }
}