import 'package:flutter/material.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/models/pryv/authentication/authentication_response_model.dart';
import 'package:hemerapp/models/pryv/service_info_model.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
import 'package:hemerapp/repositories/pryv_repository.dart';
import 'package:hemerapp/ui/components/webview.dart';
import 'package:provider/provider.dart';

class PryvProvider with ChangeNotifier {
  final _repository = PryvRepository();
  bool isLoading = false;
  bool isBack = false;

  late ServiceInfoModel _serviceInfo;

  ServiceInfoModel get serviceInfo => _serviceInfo;
  late String authUrl;

  late String pollUrl;

  Future<void> initiateLogin(BotModel bot, context) async {
    isLoading = true;
    notifyListeners();
    ServiceInfoModel serviceInfo = await _repository.fetchServiceInfo();
    final String accessUrl = serviceInfo.access;
    AuthenticationResponseModel authenticationResponseModel =
        await _repository.postAuthenticationRequest(
            accessUrl, bot.name, bot.requiredPermissions);
    authUrl = authenticationResponseModel.authUrl;
    pollUrl = authenticationResponseModel.poll;
    if (context.mounted) {
      await Navigator.push(
          context,
          MaterialPageRoute(
              builder: (context) => WebView(
                    url: authUrl,
                    pollUrl: pollUrl,
                    botName: bot.name,
                  )));
    }
  }

  Future<bool> pollAuthenticationResult(botName, context) async {
    var (username, token) = await _repository.pollAuthenticationResult(pollUrl, botName);
    Provider.of<SecureStorageProvider>(context, listen: false).addCredentials(botName, token, username);
    return username != null && token != null;
  }
}
