import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:hemerapp/providers/pryv_provider.dart';
import 'package:provider/provider.dart';
import 'package:webview_flutter/webview_flutter.dart';

class WebView extends StatefulWidget {
  const WebView(
      {super.key,
      required this.url,
      required this.pollUrl,
      required this.botName});

  final String url;
  final String pollUrl;
  final String botName;

  @override
  WebViewState createState() => WebViewState();
}

class WebViewState extends State<WebView> {
  late Future<bool> _isAuthGranted;
  bool isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _isAuthGranted = _checkAuth(widget.pollUrl, widget.botName);
  }

  _buildController(String url) {
    return WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0x00000000))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {},
          onPageStarted: (String url) {},
          onPageFinished: (String url) {},
          onWebResourceError: (WebResourceError error) {},
          onNavigationRequest: (NavigationRequest request) {
            return NavigationDecision.navigate;
          },
          onUrlChange: (UrlChange urlChange) {},
        ),
      )
      ..loadRequest(Uri.parse(url));
  }

  Future<bool> _checkAuth(String url, String botName) async {
    return Provider.of<PryvProvider>(context, listen: false)
        .pollAuthenticationResult(botName, context);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
        future: _isAuthGranted,
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            if (snapshot.data!) {
              SchedulerBinding.instance.addPostFrameCallback((_) {
                Navigator.of(context).pushNamed('/chat');
              });
            } else if (!isRefreshing) {
              isRefreshing = true;
              SchedulerBinding.instance
                  .addPostFrameCallback((_) => setState(() {
                        _isAuthGranted =
                            _checkAuth(widget.pollUrl, widget.botName);
                      }));
            }
          }
          return Scaffold(
            body: WebViewWidget(controller: _buildController(widget.url)),
          );
        });
  }
}
