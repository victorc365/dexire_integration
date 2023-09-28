import 'package:flutter/material.dart';
import 'package:hemerapp/providers/bots_provider.dart';
import 'package:hemerapp/providers/messages_provider.dart';
import 'package:hemerapp/providers/pryv_provider.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
import 'hemerapp.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart';

void main() async {
  await dotenv.load(fileName: '.env');
  runApp(MultiProvider(providers: [
    ChangeNotifierProvider(create: (_) => BotsProvider()),
    ChangeNotifierProvider(create: (_) => PryvProvider()),
    ChangeNotifierProvider(create: (_) => MessagesProvider()),
    ChangeNotifierProvider(create: (_) => SecureStorageProvider()),
  ], child: const Hemerapp()));
}
