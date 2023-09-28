import 'package:flutter/material.dart';
import 'package:hemerapp/ui/chat/chats_route.dart';
import 'package:hemerapp/ui/profile/profile_route.dart';
import 'package:hemerapp/ui/settings/settings_route.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class RootRoute extends StatefulWidget {
  const RootRoute({super.key});

  @override
  State<StatefulWidget> createState() => _RootRouteState();
}

class _RootRouteState extends State<RootRoute> {
  int currentIndex = 0;
  final screens = [
    const ChatsRoute(),
    const ProfileRoute(),
    const SettingsRoute()
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: currentIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: (value) => setState(() => currentIndex = value),
        unselectedItemColor: Colors.grey.shade600,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600),
        unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600),
        type: BottomNavigationBarType.fixed,
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.message),
            label: AppLocalizations.of(context)!.chats,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.person),
            label: AppLocalizations.of(context)!.profile,
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.settings),
            label: AppLocalizations.of(context)!.settings,
          )
        ],
      ),
    );
  }
}
