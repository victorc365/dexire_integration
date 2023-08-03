import 'dart:convert';
import 'dart:io';
import 'dart:core';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:hemerapp/models/pryv/authentication/authentication_request_model.dart';
import 'package:hemerapp/models/pryv/authentication/authentication_response_model.dart';
import 'package:hemerapp/models/pryv/authentication/poll_authorization_result_model.dart';
import 'package:hemerapp/models/pryv/authentication/requested_permission_model.dart';
import 'package:hemerapp/models/pryv/service_info_model.dart';
import 'package:http/http.dart' as http;

final String _pryvApiUrl =
    dotenv.get('PRYV_API_URL', fallback: 'localhost:8080');

// TODO - Check with Davide if we ask consent once for all bot or once per bot
// In the second case, app identifier should be the name of the bot
final String _pryvAppIdentifier =
    dotenv.get('PRYV_APP_IDENTIFIER', fallback: 'hemerapp');
const String serviceInfoEndpoint = '/service/info';
const Map<String, String> _headers = {
  HttpHeaders.contentTypeHeader: 'application/json'
};

Future<ServiceInfoModel> fetchServiceInfo() async {
  final url = 'reg.$_pryvApiUrl';
  final uri = Uri.https(url, serviceInfoEndpoint, null);
  final response = await http.get(uri);
  if (response.statusCode == HttpStatus.ok) {
    return ServiceInfoModel.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to load pryv service info');
  }
}

Future<AuthenticationResponseModel> postAuthenticationRequest(
    String url) async {
  String endpoint = '';

  if (url.contains("https://")) {
    url = url.replaceAll("https://", "");
  }
  if (url.contains("/")) {
    endpoint = url.substring(url.indexOf("/"), url.length);
    url = url.substring(0, url.indexOf("/"));
  }

  // TODO - Check with Davide from where those permissions should come.
  List<RequestedPermissionModel> requestedPermissions = [
    RequestedPermissionModel("test", "read", "test")
  ];
  final data = jsonEncode(
      AuthenticationRequestModel(_pryvAppIdentifier, requestedPermissions));
  final uri = Uri.https(url, endpoint, null);
  final response = await http.post(uri, body: data, headers: _headers);
  if (response.statusCode == HttpStatus.created) {
    return AuthenticationResponseModel.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to load pryv service info');
  }
}

Future<bool> pollAuthenticationResult(String url) async {
  String endpoint = '';
  if (url.contains("https://")) {
    url = url.replaceAll("https://", "");
  }
  if (url.contains("/")) {
    endpoint = url.substring(url.indexOf("/"), url.length);
    url = url.substring(0, url.indexOf("/"));
  }

  final uri = Uri.https(url, endpoint, null);
  while (true) {
    final response = await http.get(uri);

    if (response.statusCode == HttpStatus.ok) {
      PollAuthorizationResultModel model = PollAuthorizationResultModel.fromJson(jsonDecode(response.body));
      if (model.status == PollAuthorizationResultModel.accepted) {
        return true;
      } else if(model.status != PollAuthorizationResultModel.needSignIn) {
      }
    } else if (response.statusCode == HttpStatus.forbidden) {
      return false;

    }
  }
}
