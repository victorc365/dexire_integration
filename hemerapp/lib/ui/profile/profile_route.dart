import 'package:flutter/material.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class ProfileRoute extends StatelessWidget {
  const ProfileRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.only(left: 16, right: 16, top: 10),
              child: Row(
                children: [
                  Text(
                    AppLocalizations.of(context)!.profile,
                    style: const TextStyle(
                        fontSize: 32, fontWeight: FontWeight.bold),
                  ),

                ],
              ),
            ),
          ),
          ElevatedButton(
              onPressed: () {
                Provider.of<SecureStorageProvider>(context, listen: false)
                    .removeAllCredentials();
              },
              child: const Text("logout")),],
      ),
    );
  }
}
