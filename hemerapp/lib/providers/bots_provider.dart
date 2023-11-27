import 'package:flutter/material.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';

class BotsProvider with ChangeNotifier {
  final _repository = BotsRepository();
  bool isLoading = false;
  BotModel? currentBot;
  List<BotModel> _bots = [];
  List<BotModel> _contacts = [];

  List<BotModel> get bots => _bots;

  List<BotModel> get contacts => _contacts;

  Future<void> getAllBots(String? username) async {
    isLoading = true;
    notifyListeners();
    _bots = await _repository.fetchBots();
    if (username != null) {
      _contacts = await _repository.fetchContacts(username);
    }

    isLoading = false;
    notifyListeners();
  }
}
