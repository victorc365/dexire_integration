import 'package:flutter/material.dart';
import 'package:hemerapp/ui/components/side_menu.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class RootRoute extends StatelessWidget {
  final Widget child;
  const RootRoute({super.key, required this.child});

  @override
Widget build(BuildContext context) {
    return Scaffold(
      drawer: const SideMenu(),
      appBar: AppBar(title: Text(AppLocalizations.of(context)!.appName),),
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