import 'package:flutter/material.dart';

class ImageMessage extends StatelessWidget {
  const ImageMessage({super.key, required this.imageUrl, this.description,required this.isUser});

  final String? description;
  final bool isUser;
  final String imageUrl;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(left: 14, right: 14, top: 10, bottom: 10),
      child: Align(
        alignment: isUser ? Alignment.topLeft : Alignment.topRight,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            color: isUser ? Colors.grey.shade200 : Colors.blue[200],
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Image.network(
                    imageUrl,
                    width: 200, // Adjust the width as needed
                    height: 150, // Adjust the height as needed
                    fit: BoxFit.cover,
                  )
                )
                // Image Widget
                ,
                const SizedBox(height: 8), // Adjust the spacing as needed
                // Optional Text Description
                if (description != null)
                  Text(
                    description!,
                    style: const TextStyle(fontSize: 15),
                  ),
              ],
            ),

        ),
      ),
    );
  }
}