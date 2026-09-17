import 'package:flutter/material.dart';
import 'data/user_settings.dart';
import 'screens/auth_screen.dart';
import 'screens/main_navigation_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const MalaysiaTourismApp());
}

class MalaysiaTourismApp extends StatelessWidget {
  const MalaysiaTourismApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JalanJalan 2026',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        // 全局主题色不再有深绿，主要使用珊瑚红和深靛蓝
        primaryColor: const Color(0xFFE07A5F),
        scaffoldBackgroundColor: const Color(0xFFF4F1DE),
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFFE07A5F)),
      ),
      // 动态监听登录状态，未登录进 Login，已登录进 Home
      home: ValueListenableBuilder<bool>(
        valueListenable: UserSettings.instance.isLoggedIn,
        builder: (context, isLoggedIn, _) {
          if (isLoggedIn) {
            return const MainNavigationScreen();
          } else {
            return const AuthScreen(initialIsLogin: true);
          }
        },
      ),
    );
  }
}