import 'package:flutter/material.dart';
import 'package:hemerapp/hemerapp.dart';

class SettingsRoute extends StatefulWidget {
  const SettingsRoute({super.key});

  @override
  State<StatefulWidget> createState() => _SettingsRouteState();
}

class _SettingsRouteState extends State<SettingsRoute> {
  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body:  Center(
        child: Column(
          children: [
            Row(
              children: [
                LanguageButton(languageCode: 'en',),
                LanguageButton(languageCode: 'fr',),
                LanguageButton(languageCode: 'de',),
                LanguageButton(languageCode: 'it',),
              ],
            )
          ],
        ),
      ),
    );
  }
}

class LanguageButton extends StatelessWidget {
  const LanguageButton({
    super.key,
    required this.languageCode,
  });
  final String languageCode;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      child: Text(languageCode.toUpperCase()),
      onPressed: () {
        Hemerapp.of(context).setLocale(
            Locale.fromSubtags(languageCode: languageCode));
      },
    );
  }
}
