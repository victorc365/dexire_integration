import 'package:flutter/material.dart';
import 'package:hemerapp/ui/bots/bots_route.dart';
import 'package:hemerapp/ui/login/login_route.dart';
import 'package:hemerapp/ui/profile/profile_route.dart';
import 'package:hemerapp/ui/root/root_route.dart';

class Hemerapp extends StatelessWidget {
  const Hemerapp({Key? key}) : super(key:key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hemerapp',
      initialRoute: '/bots',
      routes: {
        '/bots': (context) => const RootRoute(child: BotsRoute()),
        '/login': (context) => const RootRoute(child: LoginRoute()),
        '/profile': (context) => const RootRoute(child: ProfileRoute()),
      },
    );
  }
}