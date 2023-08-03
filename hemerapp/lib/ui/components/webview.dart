import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:hemerapp/repositories/pryv_repository.dart';
import 'package:webview_flutter/webview_flutter.dart';

class WebView extends StatefulWidget {
  const WebView({super.key, required this.url, required this.pollUrl});
  final String url;
  final String pollUrl;
  @override
  WebViewState createState() => WebViewState();
}

class WebViewState extends State<WebView> {
  late Future<bool> _isAuthGranted;
  bool isRefreshing = false;
  @override
  void initState() {
    super.initState();
    _isAuthGranted = _checkAuth(widget.pollUrl);
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

  Future<bool> _checkAuth(String url) async {
    return pollAuthenticationResult(url);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<bool>(
        future: _isAuthGranted,
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            if (snapshot!.data!) {
              Navigator.pushNamed(context, '/chat');
            } else if(!isRefreshing){
              isRefreshing = true;
              SchedulerBinding.instance.addPostFrameCallback((_) => setState(() {
                _isAuthGranted = _checkAuth(widget.pollUrl);
              }));
            }
          }
          return Scaffold(
            body: WebViewWidget(controller: _buildController(widget.url)),
          );
        });
  }
}
