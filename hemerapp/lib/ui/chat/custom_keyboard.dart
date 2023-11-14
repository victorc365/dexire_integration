import 'package:flutter/material.dart';
import 'package:hemerapp/providers/messages_provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class CustomKeyboard extends StatelessWidget {
  final TextEditingController textController;
  final Function handleSubmitted;
  final MessagesProvider messagesProvider;
  final List<String>? options;
  const CustomKeyboard(
      {super.key, required this.textController, required this.handleSubmitted, required this.messagesProvider, required this.options});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.bottomLeft,
      child: Container(
        padding: const EdgeInsets.only(left: 10, bottom: 10, top: 10),
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
                  keyboardType: options == null? TextInputType.text: TextInputType.none,
                  controller: textController,
                  decoration: InputDecoration(
                      hintText: AppLocalizations.of(context)!.hintKeyboard,
                      hintStyle: const TextStyle(color: Colors.black54),
                      border: InputBorder.none),
                )),
            const SizedBox(
              width: 15,
            ),
            FloatingActionButton(
              onPressed: () {
                handleSubmitted(textController.text, messagesProvider);
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
    );
  }
}



class CustomPad extends StatelessWidget {
  const CustomPad({super.key});

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    throw UnimplementedError();
  }

}