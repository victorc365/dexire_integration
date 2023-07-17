import 'package:flutter/material.dart';

class SideMenu extends StatelessWidget {
  const SideMenu({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SingleChildScrollView(
        child: Column(
          children: [
            DrawerHeader(
                child: Image.asset("assets/images/aislab.png"),
            ),
            DrawerListTile(
              title: 'Bots',
              press: () {
                Navigator.pushNamed(context, '/bots');
              },
              icon: Icons.smart_toy,
            ),
            DrawerListTile(
              title: 'Profile',
              press: () {
                Navigator.pushNamed(context, '/profile');
              },
              icon: Icons.person,
            ),
            DrawerListTile(
              title: 'Logout',
              press: () {
                //TODO - implement logout
              },
              icon: Icons.exit_to_app,
            )
          ],
        ),
      ),
    );
  }
}

class DrawerListTile extends StatelessWidget {
  const DrawerListTile({
    super.key,
    required this.title,
    required this.icon,
    required this.press,
  });

  final String title;
  final IconData icon;
  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: press,
      leading: Icon(icon),
      title: Text(title),
    );
  }
}
