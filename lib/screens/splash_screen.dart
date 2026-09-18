import 'package:flutter/material.dart';
import 'main_navigation_screen.dart';
import '../data/mock_events.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacity;
  late Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    _opacity = Tween<double>(begin: 1.0, end: 0.0).animate(
      CurvedAnimation(parent: _controller, curve: const Interval(0.6, 1.0, curve: Curves.easeOut)),
    );
    _scale = Tween<double>(begin: 1.0, end: 1.15).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );

    MockEventRepository.fetchEventsFromBackend();
    
    // 停留 1.2 秒后启动扩散散开动画
    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        _controller.forward().then((_) {
          Navigator.pushReplacement(
            context,
            PageRouteBuilder(
              pageBuilder: (_, _, _) => const MainNavigationScreen(),
              transitionsBuilder: (_, animation, _, child) {
                return FadeTransition(opacity: animation, child: child);
              },
              transitionDuration: const Duration(milliseconds: 600),
            ),
          );
        });
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF060B13),
      body: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Opacity(
            opacity: _opacity.value,
            child: Transform.scale(
              scale: _scale.value,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: const Color(0xFF007A3D).withValues(alpha: 0.2),
                        border: Border.all(color: const Color(0xFF00FF9D), width: 2),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF00FF9D).withValues(alpha: 0.3),
                            blurRadius: 30,
                            spreadRadius: 4,
                          ),
                        ],
                      ),
                      child: const Icon(Icons.explore, size: 50, color: Color(0xFF00FF9D)),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'VISIT MALAYSIA',
                      style: TextStyle(
                        color: Color(0xFFF8FAFC),
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 3.0,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'CULTURAL DISCOVERY & ECO-HERITAGE',
                      style: TextStyle(
                        color: Color(0xFF00FF9D),
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}