import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/models/message_model.dart';
import 'package:hemerapp/providers/bots_provider.dart';
import 'package:hemerapp/providers/messages_provider.dart';
import 'package:hemerapp/providers/pryv_provider.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
import 'package:hemerapp/ui/chat/custom_keyboard.dart';
import 'package:hemerapp/ui/feedback/feedback_dialog.dart';
import 'package:hemerapp/ui/profile/profile_dialog.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

import 'dart:developer' as developer;

class ChatRoute extends StatefulWidget {
  const ChatRoute({super.key});

  @override
  ChatRouteState createState() => ChatRouteState();
}

class ChatRouteState extends State<ChatRoute> {
  String username = '';
  String botStatus = '';
  BotModel? bot;
  List<String>? options;
  late MessagesProvider messagesProvider;
  final TextEditingController _textController = TextEditingController();
  final ScrollController _controller = ScrollController();

  void _handleSubmitted(String text, MessagesProvider messagesProvider) {
    _textController.clear();
    if (text.isNotEmpty) {
      MessageModel message =
          MessageModel('${bot?.name}_$username', username, text, null, null);
      messagesProvider.sendMessage(message);
    }
  }

  @override
  void initState() {
    super.initState();
    bot = Provider.of<BotsProvider>(context, listen: false).currentBot;
    WidgetsBinding.instance.addPostFrameCallback((timeStamp) {
      Provider.of<SecureStorageProvider>(context, listen: false)
          .getCredentials(bot?.name)
          .then((_) {
        final secureStorage =
            Provider.of<SecureStorageProvider>(context, listen: false);
        if (secureStorage.isLoginRequired) {
          Provider.of<PryvProvider>(context, listen: false)
              .initiateLogin(bot!, context);
        } else {
          final token = secureStorage.token;
          username = secureStorage.username!;
          Provider.of<MessagesProvider>(context, listen: false)
              .openChannel(username, bot?.name, token);
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<SecureStorageProvider>(builder: (context, value, child) {
      if (value.isLoading) {
        return const Center(
          child: CircularProgressIndicator(),
        );
      }

      return Scaffold(
        appBar: _buildAppBar(context),
        body: Consumer<MessagesProvider>(
          builder: (context, value, child) {
            if (value.isLoading) {
              SchedulerBinding.instance.addPostFrameCallback((timeStamp) {
                setState(() {
                  botStatus = AppLocalizations.of(context)!.offline;
                });
              });

              return const Center(
                child: CircularProgressIndicator(),
              );
            }

            SchedulerBinding.instance.addPostFrameCallback((timeStamp) {
              if (botStatus == AppLocalizations.of(context)!.offline) {
                setState(() {
                  botStatus = AppLocalizations.of(context)!.online;
                });
              }
              _controller.jumpTo(_controller.position.maxScrollExtent);
            });

            final List<MessageModel> messages = value.messages;
            return Column(
              children: [
                //chat bubble view
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      FocusScope.of(context).unfocus();
                    },
                    child: ListView.builder(
                        controller: _controller,
                        itemCount: value.messages.length,
                        itemExtent: null,
                        shrinkWrap: true,
                        physics: const BouncingScrollPhysics(),
                        itemBuilder: ((context, index) {
                          return Container(
                            padding: const EdgeInsets.only(
                                left: 14, right: 14, top: 10, bottom: 10),
                            child: Align(
                              alignment:
                                  messages[index].to == username.toLowerCase()
                                      ? Alignment.topLeft
                                      : Alignment.topRight,
                              child: Container(
                                decoration: BoxDecoration(
                                    borderRadius: BorderRadius.circular(20),
                                    color: (messages[index].to ==
                                            username.toLowerCase())
                                        ? Colors.grey.shade200
                                        : Colors.blue[200]),
                                padding: const EdgeInsets.all(16),
                                child: Text(
                                  messages[index].body!,
                                  style: const TextStyle(fontSize: 15),
                                ),
                              ),
                            ),
                          );
                        })),
                  ),
                ),
                CustomKeyboard(
                  textController: _textController,
                  handleSubmitted: _handleSubmitted,
                  messagesProvider: value,
                  options: options,
                )
              ],
            );
          },
        ),
      );
    });
  }

  AppBar _buildAppBar(BuildContext context) {
    return AppBar(
      actions: [
        PopupMenuButton<MenuItem>(
            onSelected: (value) {
              switch (value) {
                case MenuItem.profile:
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return ProfileDialog();
                    },
                  );
                  break;
                case MenuItem.feedback:
                  showDialog(
                    context: context,
                    builder: (BuildContext context) {
                      return FeedbackDialog();
                    },
                  );
                  break;
                case MenuItem.delete:
                  break;
                case MenuItem.logout:
                  Provider.of<SecureStorageProvider>(context, listen: false)
                      .removeCredentials(bot?.name);
                  Navigator.of(context).pushNamed('/');
                  break;
              }
            },
            itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: MenuItem.profile,
                    child: Text('My Profile'),
                  ),
                  const PopupMenuItem(
                    value: MenuItem.feedback,
                    child: Text('Feedback'),
                  ),
                  const PopupMenuItem(
                    value: MenuItem.logout,
                    child: Text('Log out'),
                  ),
                  const PopupMenuItem(
                    value: MenuItem.delete,
                    child: Text('Delete'),
                  ),
                ]),
      ],
      iconTheme: const IconThemeData(color: Colors.black),
      elevation: 0,
      automaticallyImplyLeading: false,
      backgroundColor: Colors.white,
      flexibleSpace: SafeArea(
          child: Container(
        padding: const EdgeInsets.only(
          right: 16,
        ),
        child: Row(
          children: [
            IconButton(
              onPressed: () {
                Navigator.of(context).pushNamed('/');
              },
              icon: const Icon(
                Icons.arrow_back,
                color: Colors.black,
              ),
            ),
            const SizedBox(
              width: 2,
            ),
            CircleAvatar(
              backgroundImage: bot?.icon != null
                  ? NetworkImage(bot!.icon!)
                  : Image.asset("assets/images/defaultBotIcon.png").image,
              maxRadius: 20,
            ),
            const SizedBox(
              width: 12,
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    bot!.name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(
                    height: 6,
                  ),
                  Text(
                    botStatus,
                    style: TextStyle(
                      color: Colors.grey.shade600,
                      fontSize: 13,
                    ),
                  )
                ],
              ),
            ),
          ],
        ),
      )),
    );
  }
}

enum MenuItem { profile, feedback, logout, delete }
