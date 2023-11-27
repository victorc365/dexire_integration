import 'package:flutter/material.dart';
import 'package:hemerapp/hemerapp.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class SettingsRoute extends StatefulWidget {
  const SettingsRoute({super.key});

  @override
  State<StatefulWidget> createState() => _SettingsRouteState();
}

class _SettingsRouteState extends State<SettingsRoute> {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.only(left: 16, right: 16, top: 10),
            child: Row(
              children: [
                Text(
                  AppLocalizations.of(context)!.settings,
                  style: const TextStyle(
                      fontSize: 32, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(left: 16, top: 32, right: 16),
          child: Column(
            children: [
              Row(
                children: [
                  Text(
                    AppLocalizations.of(context)!.languages,
                    style: const TextStyle(
                        fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const Row(
                children: [
                  LanguageButton(
                    languageCode: 'en',
                  ),
                  LanguageButton(
                    languageCode: 'fr',
                  ),
                  LanguageButton(
                    languageCode: 'de',
                  ),
                  LanguageButton(
                    languageCode: 'it',
                  ),
                ],
              )
            ],
          ),
        ),
      ],
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
        Hemerapp.of(context)
            .setLocale(Locale.fromSubtags(languageCode: languageCode));
      },
    );
  }
}
