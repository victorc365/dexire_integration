import 'package:flutter/material.dart';
import 'package:hemerapp/providers/bots_provider.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

import 'conversation.dart';

class ChatsRoute extends StatefulWidget {
  const ChatsRoute({super.key});

  @override
  State<ChatsRoute> createState() => _ChatsRouteState();
}

class _ChatsRouteState extends State<ChatsRoute> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((timeStamp) {
      Provider.of<BotsProvider>(context, listen: false).getAllBots();
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.only(left: 16, right: 16, top: 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    AppLocalizations.of(context)!.conversations,
                    style: const TextStyle(
                        fontSize: 32, fontWeight: FontWeight.bold),
                  ),
                  InkWell(
                    onTap: () => Navigator.of(context).pushNamed('/contacts'),
                    child: Container(
                      height: 30,
                      decoration: BoxDecoration(
                          color: Colors.pinkAccent[50],
                          borderRadius: BorderRadius.circular(30)),
                      padding: const EdgeInsets.only(
                          left: 8, right: 8, top: 2, bottom: 2),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.add,
                            color: Colors.pinkAccent,
                            size: 20,
                          ),
                          const SizedBox(
                            width: 2,
                          ),
                          Text(AppLocalizations.of(context)!.addNew,
                              style: const TextStyle(
                                  fontSize: 14, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  )
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(left: 16, top: 16, right: 16),
            child: TextField(
              decoration: InputDecoration(
                  hintText: AppLocalizations.of(context)!.hintSearch,
                  hintStyle: TextStyle(color: Colors.grey.shade600),
                  prefixIcon: Icon(
                    Icons.search,
                    color: Colors.grey.shade600,
                    size: 20,
                  ),
                  filled: true,
                  fillColor: Colors.grey.shade100,
                  contentPadding: const EdgeInsets.all(8),
                  enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(20),
                      borderSide: BorderSide(color: Colors.grey.shade100))),
            ),
          ),
          Consumer<BotsProvider>(
            builder: (context, value, child) {
              if (value.isLoading) {
                return const Center(
                  child: CircularProgressIndicator(),
                );
              }
              final bots = value.bots;
              return ListView.builder(
                itemCount: bots.length,
                shrinkWrap: true,
                padding: const EdgeInsets.only(top: 16),
                physics: const NeverScrollableScrollPhysics(),
                itemBuilder: ((context, index) {
                  return GestureDetector(
                    onTap: (() => Navigator.of(context)
                        .pushNamed('/chat', arguments: bots[index])),
                    child: ConversationList(
                        name: bots[index].name,
                        messageText: "test",
                        imageURL: bots[index].icon,
                        isMessageRead:
                            (index == 0 || index == 3) ? true : false,
                        time: 'yesterday'),
                  );
                }),
              );
            },
          )
        ],
      ),
    );
  }
}
