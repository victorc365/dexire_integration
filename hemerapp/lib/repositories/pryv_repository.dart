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

class PryvRepository {
  late String _pryvApiUrl;
  String serviceInfoEndpoint = '/service/info';
  late Map<String, String> _headers;

  PryvRepository() {
    _pryvApiUrl = dotenv.get('PRYV_API_URL', fallback: 'localhost:8080');
    _headers = {HttpHeaders.contentTypeHeader: 'application/json'};
  }

  (String, String) handlePryvUrl(url) {
    String endpoint = '';
    if (url.contains("https://")) {
      url = url.replaceAll("https://", "");
    }
    if (url.contains("/")) {
      endpoint = url.substring(url.indexOf("/"), url.length);
      url = url.substring(0, url.indexOf("/"));
    }
    return (url, endpoint);
  }

  Future<AuthenticationResponseModel> postAuthenticationRequest(
      String url,
      String botName,
      List<RequestedPermissionModel> requestedPermissions) async {
    String endpoint = '';

    (url, endpoint) = handlePryvUrl(url);

    final data =
        jsonEncode(AuthenticationRequestModel(botName, requestedPermissions));
    final uri = Uri.https(url, endpoint, null);
    final response = await http.post(uri, body: data, headers: _headers);
    if (response.statusCode == HttpStatus.created) {
      return AuthenticationResponseModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to authentication request');
    }
  }

  Future<(String?, String?)> pollAuthenticationResult(
      String url, String botName) async {
    String endpoint = '';
    (url, endpoint) = handlePryvUrl(url);

    final uri = Uri.https(url, endpoint, null);
    while (true) {
      final response = await http.get(uri);

      if (response.statusCode == HttpStatus.ok) {
        PollAuthorizationResultModel model =
            PollAuthorizationResultModel.fromJson(jsonDecode(response.body));
        if (model.status == PollAuthorizationResultModel.accepted) {
          final connectionInfo =
              model.apiEndpoint!.replaceAll("https://", "").split("@");
          final token = connectionInfo[0];
          final username = connectionInfo[1].split('.')[0];

          return (username, token);
        } else if (model.status != PollAuthorizationResultModel.needSignIn) {}
      } else if (response.statusCode == HttpStatus.forbidden) {
        return (null, null);
      }
    }
  }

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
}
