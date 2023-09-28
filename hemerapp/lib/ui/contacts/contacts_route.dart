import 'package:flutter/material.dart';
import 'package:hemerapp/providers/bots_provider.dart';
import 'package:hemerapp/ui/chat/conversation.dart';
import 'package:provider/provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class ContactsRoute extends StatefulWidget {
  const ContactsRoute({super.key});

  @override
  State<ContactsRoute> createState() => _ContactsRouteState();
}

class _ContactsRouteState extends State<ContactsRoute> {
  String searchQuery = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((timeStamp) {
      Provider.of<BotsProvider>(context, listen: false).getAllBots();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        child: Column(
          children: [
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.only(left: 16, right: 16, top: 10),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    IconButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                      },
                      icon: const Icon(
                        Icons.arrow_back,
                        color: Colors.black,
                      ),
                    ),
                    Text(
                      AppLocalizations.of(context)!.contacts,
                      style: const TextStyle(
                          fontSize: 32, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.only(left: 16, top: 16, right: 16),
              child: TextField(
                onChanged: (value) => setState(() {
                  searchQuery = value;
                }),
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

                var bots = value.bots;
                if (searchQuery.isNotEmpty) {
                  bots = bots
                      .where((bot) => bot.name
                          .toLowerCase()
                          .contains(searchQuery.toLowerCase()))
                      .toList();
                }
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
                          isMessageRead: null,
                          time: null),
                    );
                  }),
                );
              },
            )
          ],
        ),
      ),
    );
  }
}
