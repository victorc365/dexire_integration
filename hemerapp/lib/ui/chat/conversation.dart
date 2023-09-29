import 'package:flutter/material.dart';

class ConversationList extends StatefulWidget {
  final String name;
  final String messageText;
  final String? imageURL;
  final String? time;
  final bool? isMessageRead;

  const ConversationList(
      {super.key,
      required this.name,
      required this.messageText,
      required this.imageURL,
      required this.isMessageRead,
      required this.time});

  @override
  State<ConversationList> createState() => _ConversationListState();
}

class _ConversationListState extends State<ConversationList> {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(
        left: 16,
        right: 16,
        top: 10,
        bottom: 10,
      ),
      child: Row(
        children: [
          Expanded(
            child: Row(
              children: [
                CircleAvatar(
                  backgroundImage: widget.imageURL != null
                      ? NetworkImage(widget.imageURL!)
                      : Image.asset("assets/images/defaultBotIcon.png").image,
                  maxRadius: 30,
                ),
                const SizedBox(
                  width: 16,
                ),
                Expanded(
                    child: Container(
                  color: Colors.transparent,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.name,
                        style: const TextStyle(fontSize: 16),
                      ),
                      const SizedBox(
                        height: 6,
                      ),
                      Text(
                        widget.messageText,
                        style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey.shade600,
                            fontWeight: widget.isMessageRead != null &&
                                    widget.isMessageRead!
                                ? FontWeight.bold
                                : FontWeight.normal),
                      )
                    ],
                  ),
                ))
              ],
            ),
          ),
          if (widget.time != null)
            Text(
              widget.time!,
              style: TextStyle(
                fontSize: 12,
                fontWeight:
                    widget.isMessageRead != null && widget.isMessageRead!
                        ? FontWeight.bold
                        : FontWeight.normal,
              ),
            )
        ],
      ),
    );
  }
}
