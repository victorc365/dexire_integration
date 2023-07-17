import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:hemerapp/ui/bots/bots_route.dart';
import 'package:hemerapp/ui/login/login_route.dart';
import 'package:hemerapp/ui/profile/profile_route.dart';
import 'package:hemerapp/ui/root/root_route.dart';
import 'package:hemerapp/ui/settings/settings_route.dart';

class Hemerapp extends StatefulWidget {
  const Hemerapp({Key? key}) : super(key:key);

  static of(BuildContext context, {bool root = false}) => root
      ? context.findRootAncestorStateOfType<_HemerappState>()
      : context.findAncestorStateOfType<_HemerappState>();

  @override
  State<StatefulWidget> createState() => _HemerappState();
}

class _HemerappState extends State<Hemerapp> {
  Locale _locale = const Locale.fromSubtags(languageCode: 'en');
  void setLocale(Locale value) => setState(() => _locale = value);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hemerapp',
      locale: _locale,
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
        '/settings': (context) => const RootRoute(child: SettingsRoute())
      },
    );
  }
}