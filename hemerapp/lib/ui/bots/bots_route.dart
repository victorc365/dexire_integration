import 'package:flutter/material.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/models/pryv/authentication/authentication_response_model.dart';
import 'package:hemerapp/models/pryv/authentication/requested_permission_model.dart';
import 'package:hemerapp/models/pryv/service_info_model.dart';
import 'package:hemerapp/repositories/bots_repository.dart';
import 'package:hemerapp/repositories/pryv_repository.dart';
import 'package:hemerapp/ui/components/bot_cell.dart';
import 'package:hemerapp/ui/components/webview.dart';
import 'package:hemerapp/ui/root/root_route.dart';

class BotsRoute extends StatefulWidget {
  const BotsRoute({super.key});

  @override
  BotRouteState createState() => BotRouteState();
}

class BotRouteState extends State<BotsRoute> {
  late Future<List<BotModel>> _futureBots;

  @override
  void initState() {
    super.initState();
    _futureBots = fetchBots();
  }

  _requireAccessFromPryv(String botName, List<RequestedPermissionModel> requestedPermissions) async {
    ServiceInfoModel serviceInfo = await fetchServiceInfo();
    final String accessUrl = serviceInfo.access;
    AuthenticationResponseModel authenticationResponseModel =
        await postAuthenticationRequest(accessUrl, botName, requestedPermissions);
    String authUrl = authenticationResponseModel.authUrl;
    String pollUrl = authenticationResponseModel.poll;
    if (context.mounted) {
      await Navigator.push(
          context,
          MaterialPageRoute(
              builder: (context) => RootRoute(
                      child: WebView(
                    url: authUrl,
                    pollUrl: pollUrl,
                  ))));
    }
  }

  _buildGridView(List<BotModel> bots) {
    return Padding(
      padding: const EdgeInsets.all(5),
      child: GridView.count(
        crossAxisCount: 2,
        childAspectRatio: 1,
        mainAxisSpacing: 4,
        crossAxisSpacing: 4,
        children: bots.map((bot) {
              return Visibility(
                  visible: true,
                  child: GestureDetector(
                      child: GridTile(
                        child: BotCell(bot.name, null, 60.0),
                      ),
                      onTap: () async {
                        if (bot.isPryvRequired) {
                          await _requireAccessFromPryv(bot.name, bot.requiredPermissions);
                        }
                          if (context.mounted) {
                            Navigator.pushNamed(context, '/chat');
                          }

                      }));
            }).toList() ??
            [],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
                child: FutureBuilder<List<BotModel>>(
                    future: _futureBots,
                    builder: (context, snapshot) {
                      if (snapshot.hasData) {
                        List<BotModel> bots = snapshot.data!;
                        return _buildGridView(bots);
                      }
                      return const Center(
                        child: CircularProgressIndicator(),
                      );
                    }))
          ],
        ),
      ),
    );
  }
}
