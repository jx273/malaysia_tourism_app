import 'dart:ui';
import 'package:flutter/material.dart';
import 'home_screen.dart';
import 'my_plan_screen.dart';
import 'map_screen.dart';
import 'passport_screen.dart';
import 'settings_screen.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    MyPlanScreen(),
    MapScreen(),
    PassportScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE), 
      extendBody: true, 
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 400),
        switchInCurve: Curves.easeOutCubic,
        switchOutCurve: Curves.easeInCubic,
        transitionBuilder: (child, animation) {
          return FadeTransition(
            opacity: animation,
            child: ScaleTransition(
              scale: Tween<double>(begin: 0.98, end: 1.0).animate(animation),
              child: child,
            ),
          );
        },
        child: KeyedSubtree(
          key: ValueKey<int>(_currentIndex),
          child: _screens[_currentIndex],
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          margin: const EdgeInsets.only(left: 20, right: 20, bottom: 16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(32),
            boxShadow: [
              BoxShadow(
                color: const Color(0xFF3D405B).withValues(alpha: 0.15),
                blurRadius: 20,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(32),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.75), 
                  border: Border.all(color: Colors.white.withValues(alpha: 0.3), width: 1),
                ),
                child: BottomNavigationBar(
                  currentIndex: _currentIndex,
                  onTap: (index) => setState(() => _currentIndex = index),
                  type: BottomNavigationBarType.fixed,
                  backgroundColor: Colors.transparent,
                  elevation: 0,
                  selectedItemColor: const Color(0xFFE07A5F),
                  unselectedItemColor: const Color(0xFF3D405B).withValues(alpha: 0.4),
                  showSelectedLabels: false,
                  showUnselectedLabels: false,
                  iconSize: 26, 
                  items: [
                    _navItem(Icons.home_filled, Icons.home_outlined),
                    _navItem(Icons.calendar_today, Icons.calendar_today_outlined),
                    _navItem(Icons.explore, Icons.explore_outlined),
                    _navItem(Icons.photo_album, Icons.photo_album_outlined),
                    _navItem(Icons.person, Icons.person_outline),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  BottomNavigationBarItem _navItem(IconData active, IconData inactive) {
    return BottomNavigationBarItem(
      icon: Icon(inactive, size: 26),
      activeIcon: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: const Color(0xFFE07A5F).withValues(alpha: 0.15),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Icon(active, size: 26),
      ),
      label: '',
    );
  }
}