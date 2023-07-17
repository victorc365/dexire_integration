import 'package:flutter/material.dart';
import 'package:hemerapp/ui/components/side_menu.dart';

class RootRoute extends StatelessWidget {
  final Widget child;
  const RootRoute({super.key, required this.child});

  @override
Widget build(BuildContext context) {
    return Scaffold(
      drawer: const SideMenu(),
      appBar: AppBar(title: const Text("HermApp 3.0"),),
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