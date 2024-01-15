import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';

class ErebotRecordingButton extends StatefulWidget {
  const ErebotRecordingButton({
    Key? key,
    required this.onRecordingEnded,
  }) : super(key: key);

  final Function(String) onRecordingEnded;

  @override
  _ErebotRecordingButtonState createState() => _ErebotRecordingButtonState();
}

class _ErebotRecordingButtonState extends State<ErebotRecordingButton> {
  final SpeechToText _speechToText = SpeechToText();
  bool _speechEnabled = false;
  String message = '';

  @override
  void initState() {
    super.initState();
    _initSpeech();
  }

  void _initSpeech() async {
    _speechEnabled = await _speechToText.initialize();
    setState(() {});
  }

  void _onSpeechResult(SpeechRecognitionResult result) {
    setState(() {
      message = result.recognizedWords;
    });
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) async {
        if (_speechEnabled) {
          await _speechToText.listen(onResult: _onSpeechResult);
          setState(() {});
        }
      },
      onTapUp: (_) async {
        await _speechToText.stop();
        setState(() {});
        if (message.isNotEmpty) {
          widget.onRecordingEnded(message);
        }
      },
      child: Container(
        height: 30,
        width: 30,
        decoration: BoxDecoration(
          color: Colors.lightBlue,
          borderRadius: BorderRadius.circular(30),
        ),
        child: const Icon(
          Icons.mic,
          color: Colors.white,
          size: 20,
        ),
      ),
    );
  }
}