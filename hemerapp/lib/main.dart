import 'package:flutter/material.dart';
import 'hemerapp.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';


void main() async {
  await dotenv.load(fileName: '.env');
  runApp(const Hemerapp());
}