import 'dart:convert';
import 'dart:io';
import 'dart:core';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:hemerapp/models/bot_model.dart';

final String _erebotsApiUrl =
    dotenv.get('EREBOTS_API_URL', fallback: 'localhost:8080');
final String _erebotsApiVersion = dotenv.get('EREBOTS_API_VERSION');
final String _botsEndpoint = '/$_erebotsApiVersion/bots';

Future<List<BotModel>> fetchBots() async {
  final uri = Uri.http(_erebotsApiUrl, _botsEndpoint, null);
  final response = await http.get(uri);
  if (response.statusCode == HttpStatus.ok) {
    final parsedBots = jsonDecode(response.body).cast<Map<String, dynamic>>();
    return parsedBots.map<BotModel>((json) => BotModel.fromJson(json)).toList();
  } else {
    throw Exception("Failed to load bots");
  }
}
