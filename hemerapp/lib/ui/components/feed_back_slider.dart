import 'package:flutter/material.dart';
import 'dart:developer' as developer;

import 'package:flutter_chat_ui/flutter_chat_ui.dart';


class FeedBackSlider extends StatefulWidget {
  final double minValue;
  final double maxValue;
  final double currentValue;
  final Function buttonAction;

  const FeedBackSlider({super.key, required this.minValue, required this.maxValue,
    required this.buttonAction, this.currentValue=50});

  @override
  State<FeedBackSlider> createState() => _FeedBackSliderState();
}

class _FeedBackSliderState extends State<FeedBackSlider>{

  double _currentSliderValue = 50;

  @override
  void initState(){
    super.initState();
    _currentSliderValue = widget.currentValue;
  }


  @override
  Widget build(BuildContext context){

    return Padding(padding: const EdgeInsets.all(2.0),
    child:  Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Text("Move the slider and press the button"),
        const SizedBox(height: 20),
        Slider(
          value: _currentSliderValue,
          min: widget.minValue,
          max: widget.maxValue,
          divisions: 10,
          activeColor: Colors.blue,
          inactiveColor: Colors.white,
          label: _currentSliderValue.round().toString(),
          onChanged: (value) {
            setState(() {
              _currentSliderValue = value;
            });
          },
        ),
        const Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(
              Icons.thumb_down,
              size: 30,
              color: Colors.red,
            ),
            Icon(
              Icons.thumb_up,
              size: 30,
              color: Colors.green
            )
          ],
        ),
        const SizedBox(height: 10),
        OutlinedButton(
          style: TextButton.styleFrom(
            foregroundColor: Colors.white,
            backgroundColor: Colors.blue,
            padding: const EdgeInsets.all(10.0),
            textStyle: const TextStyle(fontSize: 20),
            shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
          ),
          onPressed: (){
            developer.log("Elevated button pressed");
            widget.buttonAction(_currentSliderValue.toString());
          },
          child: const Text("Send Feedback"),
        ),
      ],
    ),
    );
  }
}

