import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:hemerapp/models/bot_model.dart';
import 'package:hemerapp/models/message_model.dart';
import 'package:hemerapp/providers/bots_provider.dart';
import 'package:hemerapp/providers/messages_provider.dart';
import 'package:hemerapp/providers/pryv_provider.dart';
import 'package:hemerapp/providers/secure_storage_provider.dart';
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
  String content = '';
  BotModel? bot;
  late MessagesProvider messagesProvider;

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

            if (botStatus == AppLocalizations.of(context)!.offline) {
              SchedulerBinding.instance.addPostFrameCallback((timeStamp) {
                setState(() {
                  botStatus = AppLocalizations.of(context)!.online;
                });
              });
            }

            final List<MessageModel> messages = value.messages;
            return Stack(
              children: [
                //chat bubble view
                ListView.builder(
                    itemCount: messages.length,
                    itemBuilder: ((context, index) {
                      return Container(
                        padding: const EdgeInsets.only(
                            left: 14, right: 14, top: 10, bottom: 10),
                        child: Align(
                          alignment: messages[index].to == username
                              ? Alignment.topLeft
                              : Alignment.topRight,
                          child: Container(
                            decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(20),
                                color: (messages[index].to == username)
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
                Align(
                  alignment: Alignment.bottomLeft,
                  child: Container(
                    padding:
                        const EdgeInsets.only(left: 10, bottom: 10, top: 10),
                    height: 60,
                    width: double.infinity,
                    color: Colors.white,
                    child: Row(
                      children: [
                        Container(
                          height: 30,
                          width: 30,
                          decoration: BoxDecoration(
                            color: Colors.lightBlue,
                            borderRadius: BorderRadius.circular(30),
                          ),
                          child: const Icon(
                            Icons.add,
                            color: Colors.white,
                            size: 20,
                          ),
                        ),
                        const SizedBox(
                          width: 15,
                        ),
                        Expanded(
                            child: TextField(
                          onChanged: (value) => setState(() {
                            content = value;
                          }),
                          decoration: InputDecoration(
                              hintText:
                                  AppLocalizations.of(context)!.hintKeyboard,
                              hintStyle: const TextStyle(color: Colors.black54),
                              border: InputBorder.none),
                        )),
                        const SizedBox(
                          width: 15,
                        ),
                        FloatingActionButton(
                          onPressed: () {
                            if (content.isNotEmpty) {
                              MessageModel message = MessageModel(
                                  '${bot?.name}_$username',
                                  username,
                                  content,
                                  null,
                                  null);
                              value.sendMessage(message);
                              setState(() {
                                content = '';
                              });
                            }
                          },
                          backgroundColor: Colors.blue,
                          elevation: 0,
                          child: const Icon(
                            Icons.send,
                            color: Colors.white,
                            size: 18,
                          ),
                        )
                      ],
                    ),
                  ),
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
            const Icon(
              Icons.settings,
              color: Colors.black54,
            )
          ],
        ),
      )),
    );
  }
}
