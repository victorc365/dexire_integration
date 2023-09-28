import 'package:flutter/material.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';

class BotsProvider with ChangeNotifier {
  final _repository = BotsRepository();
  bool isLoading = false;
  List<BotModel> _bots = [];

  List<BotModel> get bots => _bots;

  Future<void> getAllBots() async {
    isLoading = true;
    notifyListeners();
    final response = await _repository.fetchBots();
    _bots = response;
    isLoading = false;
    notifyListeners();
  }
}
