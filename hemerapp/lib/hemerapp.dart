import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
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
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('en'),
        Locale('fr'),
        Locale('it'),
        Locale('de'),
      ],
      initialRoute: '/bots',
      routes: {
        '/bots': (context) => const RootRoute(child: BotsRoute()),
        '/login': (context) => const RootRoute(child: LoginRoute()),
        '/profile': (context) => const RootRoute(child: ProfileRoute()),
      },
    );
  }
}