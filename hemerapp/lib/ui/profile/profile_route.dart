import 'package:flutter/material.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
import 'package:provider/provider.dart';

class ProfileRoute extends StatelessWidget {
  const ProfileRoute({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const Expanded(child: Text('Profile route')),
            ElevatedButton(
                onPressed: () {
                  Provider.of<SecureStorageProvider>(context, listen: false)
                      .removeAllCredentials();
                },
                child: const Text("logout"))
          ],
        ),
      ),
    );
  }
}
