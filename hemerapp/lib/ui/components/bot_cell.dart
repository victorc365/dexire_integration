import 'package:flutter/material.dart';

class BotCell extends StatelessWidget {
  @required
  final String name;
  @required
  final String? icon;
  final double radius;

  const BotCell(this.name, this.icon, this.radius, {super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      color: Colors.white,
      child: Padding(
        padding: const EdgeInsets.all(10),
        child: Container(
          alignment: Alignment.center,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: [
              Flexible(
                child: CircleAvatar(
                  radius: radius,
                  backgroundColor: Colors.grey,
                  backgroundImage: icon != null ? NetworkImage(icon!): Image.asset("assets/images/defaultBotIcon.png").image,
                ),
              ),
              Text(
                name,
                style:
                const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
