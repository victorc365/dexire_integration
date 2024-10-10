import 'dart:developer';

import 'package:flutter/material.dart';
import 'package:hemerapp/providers/messages_provider.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'package:hemerapp/ui/chat/bot_keyboard.dart';
import 'package:hemerapp/ui/chat/erebot_recording_button.dart';
import 'package:collection/collection.dart';
import 'package:hemerapp/ui/components/feed_back_slider.dart';

import 'dart:developer' as developer;

class CustomKeyboard extends StatelessWidget {
  final TextEditingController textController;
  final Function handleSubmitted;
  final MessagesProvider messagesProvider;
  final List<Map<String, String>>? options;
  final BotKeyboard? botKeyboard;
  final Function(String) onRecordingEnded;

  const CustomKeyboard(
      {super.key,
      required this.textController,
      required this.handleSubmitted,
      required this.messagesProvider,
      required this.botKeyboard,
      required this.options,
      required this.onRecordingEnded});

  void _handleButton(buttonActionText) {
    handleSubmitted(buttonActionText, messagesProvider);
  }

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.bottomLeft,
      child: Container(
        padding: const EdgeInsets.only(left: 10, bottom: 10, top: 10, right: 10),
        height: botKeyboard != null ? 300 : 80, // quick n dirty for now BB
        width: double.infinity,
        color: Colors.white,
        child: Column(
          children: [
            if (botKeyboard == null)
            Row(
              children: [
                GestureDetector(
                  onTap: () {
                    FocusManager.instance.primaryFocus?.unfocus();
                  },
                  child: Container(
                    height: 30,
                    width: 30,
                    decoration: BoxDecoration(
                      color: Colors.lightBlue,
                      borderRadius: BorderRadius.circular(30),
                    ),
                    child: const Icon(
                      Icons.keyboard,
                      color: Colors.white,
                      size: 20,
                    ),
                  ),
                ),
                ErebotRecordingButton(onRecordingEnded: onRecordingEnded),
                const SizedBox(
                  width: 15,
                ),
                Expanded(
                    child: TextField(
                  keyboardType:
                      options == null ? TextInputType.text : TextInputType.none,
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
            if (botKeyboard != null && botKeyboard!.items != null && botKeyboard!.type == null)
              CustomPad(botKeyboard: botKeyboard!, buttonAction: _handleButton),
            if (botKeyboard != null && botKeyboard!.items != null && botKeyboard!.type != null)
              FeedBackSlider(minValue: 0.0, maxValue: 100, buttonAction: _handleButton),
          ],
        ),
      ),
    );
  }
}

class CustomPad extends StatelessWidget {
  final BotKeyboard botKeyboard;
  final Function buttonAction;

  const CustomPad(
      {super.key, required this.botKeyboard, required this.buttonAction});

  @override
  Widget build(BuildContext context) {
    List<List<dynamic>> keyboardPairs = botKeyboard.items!.slices(2).toList();

    return Column(
      children: [
        SizedBox(
          height: 200,
          child: SingleChildScrollView(
            child: Table(children: [
              ...keyboardPairs.map((pair) => _buildTableRow(pair)).toList(),
            ]),
          ),
        ),
        Padding(
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: [
              Expanded(child: _buildButton("Back", "BACK")),
              const SizedBox(width: 10,),
              Expanded(child: _buildButton("Home", "HOME", "home")),
              const SizedBox(width: 10,),
              Expanded(child: _buildButton("Continue", "CONTINUE")),

            ],
          ),
        )
      ],
    );
  }

  TableRow _buildTableRow(List<dynamic> rowElements) {
    return TableRow(children: [
      ...rowElements
          .map<Widget>(
            (val) => Padding(
              padding: const EdgeInsets.all(4.0),
              child: SizedBox(child: _buildButton(val["label"], val["action"])),
            ),
          )
          .toList(),
      if (rowElements.length < 2)
        const SizedBox() // Complete column if the last one is less than 2
    ]);
  }

  final Map<String, IconData> _categories = const {
      'home': Icons.home,
      'left_arrow': Icons.turn_left,
      'right_arrow': Icons.turn_right,
    };

  Widget _buildButton(label, action, [iconName]) {
    return OutlinedButton(
        style: TextButton.styleFrom(
          foregroundColor: Colors.white,
          backgroundColor: Colors.blue,
          padding: const EdgeInsets.all(10.0),
          textStyle: const TextStyle(fontSize: 20),
          shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
        ),
        onPressed: () {
          // get local time on the phone
          switch(action){
            case 'time_now':{
              DateTime now = DateTime.now();
              buttonAction("time: ${now.hour.toString()}:${now.minute.toString()}");
            }
            break;
            case 'time_in_one_hour':{
              DateTime now = DateTime.now();
              final oneHourLater = now.add(const Duration(hours: 1));
              buttonAction("time: ${oneHourLater.hour.toString()}:${oneHourLater.minute.toString()}");
            }
            break;
            case 'time_in_two_hours':{
              DateTime now = DateTime.now();
              final twoHourLater = now.add(const Duration(hours: 2));
              buttonAction("time: ${twoHourLater.hour.toString()}:${twoHourLater.minute.toString()}");
            }
            break;
            default: {
              buttonAction(action);
            }
            break;
          }
        },
        child: iconName == null ? Text(label): Icon(_categories[iconName]));
  }
}
