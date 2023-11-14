import 'package:flutter/material.dart';

class TextToSpeechMessage extends StatefulWidget {
  TextToSpeechMessage({Key? key}) : super(key: key);

  @override
  _TextToSpeechMessageState createState() => _TextToSpeechMessageState();
}

class _TextToSpeechMessageState extends State<TextToSpeechMessage> {
  @override
  void initState() {
  }

  @override
  Widget build(BuildContext context) => _sizerChild(context);

  Container _sizerChild(BuildContext context) => Container(
    padding: EdgeInsets.symmetric(horizontal: .8.w()),
    constraints: BoxConstraints(maxWidth: 100.w() * .8),
    decoration: BoxDecoration(
      borderRadius: BorderRadius.only(
        topLeft: Radius.circular(widget.radius),
        bottomLeft: widget.me
            ? Radius.circular(widget.radius)
            : const Radius.circular(4),
        bottomRight: !widget.me
            ? Radius.circular(widget.radius)
            : const Radius.circular(4),
        topRight: Radius.circular(widget.radius),
      ),
      color: widget.me ? widget.meBgColor : widget.contactBgColor,
    ),
    child: Padding(
      padding: EdgeInsets.symmetric(horizontal: 4.w(), vertical: 2.8.w()),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _playButton(context),
          SizedBox(width: 3.w()),
          _durationWithNoise(context),
          SizedBox(width: 2.2.w()),

          /// x2 button will be added here.
          // _speed(context),
        ],
      ),
    ),
  );
}

