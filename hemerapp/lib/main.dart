import 'package:flutter/material.dart';
import 'hemerapp.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';


void main() async {
  dotenv.load(fileName: '.env');
  runApp(const Hemerapp());
}