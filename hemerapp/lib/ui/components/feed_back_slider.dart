import 'package:flutter/material.dart';
import 'dart:developer' as developer;


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
          divisions: 5,
          label: _currentSliderValue.round().toString(),
          onChanged: (value) {
            setState(() {
              _currentSliderValue = value;
            });
          },
        ),
        const SizedBox(height: 10),
        OutlinedButton(
          onPressed: (){
            developer.log("Elevated button pressed");
            widget.buttonAction(_currentSliderValue.toString());
          },
          child: Text("Send Feedback"),
        ),
      ],
    ),
    );
  }
}

