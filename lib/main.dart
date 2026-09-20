import 'package:flutter/material.dart';
import 'data/user_settings.dart';
import 'screens/auth_screen.dart';
import 'screens/main_navigation_screen.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart'; 
import 'screens/splash_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  dotenv.load(fileName: ".env").then((_) {
    runApp(const MalaysiaTourismApp());
  });
}

class MalaysiaTourismApp extends StatelessWidget {
  const MalaysiaTourismApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JalanJalan 2026',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFFE07A5F),
        scaffoldBackgroundColor: const Color(0xFFF4F1DE),
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFE07A5F)),
      ),
      home: const SplashScreen(),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: UserSettings.instance.isLoggedIn,
      builder: (context, isLoggedIn, _) {
        if (isLoggedIn) {
          return const MainNavigationScreen();
        } else {
          return const AuthScreen(initialIsLogin: true);
        }
      },
    );
  }
}