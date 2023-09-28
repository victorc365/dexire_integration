import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:hemerapp/ui/chat/newchat_route.dart';
import 'package:hemerapp/ui/contacts/contacts_route.dart';
import 'package:hemerapp/ui/root/root_route.dart';

class Hemerapp extends StatefulWidget {
  const Hemerapp({Key? key}) : super(key: key);

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
      initialRoute: '/',
      routes: {
        '/': (context) => const RootRoute(),
        '/chat': (context) => const ChatRoute(),
        '/contacts': (context) => const ContactsRoute(),
      },
    );
  }
}
