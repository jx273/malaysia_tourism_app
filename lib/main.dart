import 'package:flutter/material.dart';
import 'screens/main_navigation_screen.dart';

void main() {
  runApp(const MalaysiaTourismApp());
}

class MalaysiaTourismApp extends StatelessWidget {
  const MalaysiaTourismApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Visit Malaysia Discovery',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF8FAFC), 
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF007A3D), 
          primary: const Color(0xFF007A3D),
          secondary: const Color(0xFFFF9E00),
          surface: Colors.white,
          onSurface: const Color(0xFF0F172A),
        ),
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF0F172A),
          centerTitle: false,
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}