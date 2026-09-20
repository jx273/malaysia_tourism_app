import 'package:flutter/material.dart';
import '../main.dart'; 
import '../data/mock_events.dart';
import '../widgets/pixel_mascot.dart';

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
    _scale = Tween<double>(begin: 1.0, end: 1.25).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );

    _loadDataAndTransition();
  }

  Future<void> _loadDataAndTransition() async {
    // 1. Fetch global event data before entering the app
    await MockEventRepository.fetchEventsFromBackend();
    
    // 2. Ensure the splash screen stays visible for at least 1.5 seconds
    await Future.delayed(const Duration(milliseconds: 1500));
    
    if (mounted) {
      _controller.forward().then((_) {
        Navigator.pushReplacement(
          context,
          PageRouteBuilder(
            pageBuilder: (_, _, _) => const AuthWrapper(),
            transitionsBuilder: (_, animation, _, child) {
              return FadeTransition(opacity: animation, child: child);
            },
            transitionDuration: const Duration(milliseconds: 600),
          ),
        );
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Widget _buildPixelBlock(Color color, double size, {double opacity = 1.0}) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withValues(alpha: opacity),
        borderRadius: BorderRadius.circular(size * 0.2), 
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final mascot1 = MascotType.values.first;
    final mascot2 = MascotType.values.length > 1 ? MascotType.values[1] : MascotType.values.first;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE), 
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
                    SizedBox(
                      width: 200, 
                      height: 180, 
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          Positioned(top: 10, left: 60, child: _buildPixelBlock(const Color(0xFFE07A5F), 14)), 
                          Positioned(top: 20, right: 60, child: _buildPixelBlock(const Color(0xFFF2CC8F), 18, opacity: 0.8)), 
                          
                          Positioned(top: 65, right: 15, child: _buildPixelBlock(const Color(0xFF81B29A), 22, opacity: 0.6)), 
                          Positioned(bottom: 50, right: 25, child: _buildPixelBlock(const Color(0xFF3D405B), 12, opacity: 0.7)), 
                          
                          Positioned(bottom: 10, right: 70, child: _buildPixelBlock(const Color(0xFFE07A5F), 16)), 
                          Positioned(bottom: 20, left: 55, child: _buildPixelBlock(const Color(0xFFF2CC8F), 26)),
                          
                          Positioned(bottom: 60, left: 15, child: _buildPixelBlock(const Color(0xFF81B29A), 15, opacity: 0.9)), 
                          Positioned(top: 50, left: 25, child: _buildPixelBlock(const Color(0xFF3D405B), 18, opacity: 0.5)), 

                          Positioned(
                            left: 50,
                            bottom: 50,
                            child: PixelMascot(type: mascot1, action: MascotAction.happy, size: 50),
                          ),
                          Positioned(
                            right: 50,
                            bottom: 50,
                            child: PixelMascot(type: mascot2, action: MascotAction.happy, size: 50),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    const Text(
                      'JALAN JALAN',
                      style: TextStyle(
                        color: Color(0xFF3D405B),
                        fontSize: 28,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 4.0,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE07A5F),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'DISCOVER MALAYSIA 2026',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          letterSpacing: 2.0,
                        ),
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