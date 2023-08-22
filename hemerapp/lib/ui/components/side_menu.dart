import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SideMenu extends StatelessWidget {
  const SideMenu({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SingleChildScrollView(
        child: Column(
          children: [
            DrawerHeader(
              child: Image.asset("assets/images/aislab.png"),
            ),
            DrawerListTile(
              title: AppLocalizations.of(context)!.bots,
              press: () {
                Navigator.pushNamed(context, '/bots');
              },
              icon: Icons.smart_toy,
            ),
            DrawerListTile(
              title: AppLocalizations.of(context)!.profile,
              press: () {
                Navigator.pushNamed(context, '/profile');
              },
              icon: Icons.person,
            ),
            DrawerListTile(
              title: AppLocalizations.of(context)!.settings,
              press: () {
                Navigator.pushNamed(context, '/settings');
              },
              icon: Icons.settings,
            ),
            DrawerListTile(
              title: AppLocalizations.of(context)!.logout,
              press: () async {
                const storage = FlutterSecureStorage();
                await storage.deleteAll();
                if (context.mounted) {
                  Navigator.pushNamed(context, '/bots');
                }
              },
              icon: Icons.exit_to_app,
            )
          ],
        ),
      ),
    );
  }
}

class DrawerListTile extends StatelessWidget {
  const DrawerListTile({
    super.key,
    required this.title,
    required this.icon,
    required this.press,
  });

  final String title;
  final IconData icon;
  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: press,
      leading: Icon(icon),
      title: Text(title),
    );
  }
}
