import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';

class TextToSpeechMessage extends StatefulWidget {
  const TextToSpeechMessage({
    Key? key,
    required this.text,
    this.duration,
    required this.isUser,
  }) : super(key: key);

  final String text;
  final String? duration;
  final bool isUser;

  @override
  _TextToSpeechMessageState createState() => _TextToSpeechMessageState();


}

class _TextToSpeechMessageState extends State<TextToSpeechMessage> {
  late FlutterTts flutterTts;

  @override
  void initState() {
    super.initState();
    flutterTts = FlutterTts();
  }

  Future<void> _speak() async {
    await flutterTts.setLanguage('en-US');
    await flutterTts.setPitch(1.0);
    await flutterTts.setSpeechRate(0.5);

    await flutterTts.speak(widget.text);
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: _speak,
      child: Container(
        padding: const EdgeInsets.only(left: 14, right: 14, top: 10, bottom: 10),
        child: Align(
          alignment: widget.isUser ? Alignment.topLeft : Alignment.topRight,
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20),
              color: widget.isUser ? Colors.grey.shade200 : Colors.blue[200],
            ),
            padding: const EdgeInsets.all(16),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Icon for audio (you can use a speaker icon, etc.)
                Icon(
                  Icons.volume_up,
                  size: 40,
                  color: Colors.black,
                ),
                SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    flutterTts.stop();
    super.dispose();
  }
}