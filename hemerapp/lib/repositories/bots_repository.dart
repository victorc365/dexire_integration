import 'dart:convert';
import 'dart:io';
import 'dart:core';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:hemerapp/models/bot_model.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class BotsRepository {
  late String _erebotsApiUrl;
  late String _erebotsWebsocketUrl;
  late String _erebotsApiVersion;
  late String _botsEndpoint;
  late Map<String, String> _headers;

  BotsRepository() {
    _erebotsApiUrl = dotenv.get('EREBOTS_API_URL', fallback: 'localhost:8080');

    _erebotsWebsocketUrl =
        dotenv.get('EREBOTS_WEBSOCKET_URL', fallback: 'localhost:8080');

    _erebotsApiVersion = dotenv.get('EREBOTS_API_VERSION');
    _botsEndpoint = '/$_erebotsApiVersion/bots';
    _headers = {HttpHeaders.contentTypeHeader: 'application/json'};
  }

  Future<List<BotModel>> fetchBots() async {
    final uri = Uri.http(_erebotsApiUrl, _botsEndpoint, null);
    final response = await http.get(uri);
    if (response.statusCode == HttpStatus.ok) {
      final parsedBots = jsonDecode(response.body).cast<Map<String, dynamic>>();
      return parsedBots
          .map<BotModel>((json) => BotModel.fromJson(json))
          .toList();
    } else {
      throw Exception("Failed to load bots");
    }
  }

  Future<String?> connectToBot(
      String botName, String username, String token) async {
    final uri =
        Uri.http(_erebotsApiUrl, '$_botsEndpoint/$botName/connect', null);
    final data = jsonEncode({'username': username, 'token': token});
    final response = await http.post(uri, body: data, headers: _headers);
    if (response.statusCode == HttpStatus.created) {
      return response.body;
    }
    return null;
  }

  Future<String> getStatus(String botUsername) async {
    final uri =
        Uri.http(_erebotsApiUrl, '$_botsEndpoint/$botUsername/status', null);
    final response = await http.get(uri, headers: _headers);
    if (response.statusCode == HttpStatus.ok) {
      return jsonDecode(response.body);
    }
    throw Exception("Unreachable endpoint");
  }

  WebSocketChannel openWebsocketChannel(String username, String botname) {
    return WebSocketChannel.connect(
        Uri.parse("$_erebotsWebsocketUrl/$username/$botname"));
  }
}
