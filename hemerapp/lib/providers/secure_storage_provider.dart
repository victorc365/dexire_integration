import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class SecureStorageProvider with ChangeNotifier {
  final _repository = const FlutterSecureStorage();
  bool isLoading = false;
  bool isLoginRequired = false;
  String? _username;

  String get username => _username!;
  String? _token;

  String get token => _token!;

  Future<void> addCredentials(botName, token, username) async {
    isLoading = true;
    notifyListeners();
    await _repository.write(key: botName, value: token);
    await _repository.write(key: 'username', value: token);
    isLoading = false;
    notifyListeners();
  }

  Future<void> getCredentials(botName) async {
    isLoading = true;
    notifyListeners();

    _token = await _repository.read(key: botName);
    _username = await _repository.read(key: 'username');

    if (_token == null || _username == null) {
      isLoginRequired = true;
    }

    isLoading = false;
    notifyListeners();
  }
}
