import 'package:flutter/material.dart';
// 注意这里引入 main.dart 里的 AuthWrapper
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

    MockEventRepository.fetchEventsFromBackend();
    
    // 停留 1.5 秒后启动扩散散开动画，然后进入 AuthWrapper 智能路由
    Future.delayed(const Duration(milliseconds: 1500), () {
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
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // 辅助函数：绘制复古马赛克像素块
  Widget _buildPixelBlock(Color color, double size, {double opacity = 1.0}) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: color.withValues(alpha: opacity),
        borderRadius: BorderRadius.circular(size * 0.2), // 微圆角的像素块
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // 智能获取你们现有的两只小动物（如果没有两只，就两边显示一样的）
    final mascot1 = MascotType.values.first;
    final mascot2 = MascotType.values.length > 1 ? MascotType.values[1] : MascotType.values.first;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE), // 奶油底色
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
                    // 1. 惊喜设计：马赛克与小动物的共舞舞台
                    SizedBox(
                      width: 140,
                      height: 120,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // 背景的散落像素块
                          Positioned(top: 10, left: 20, child: _buildPixelBlock(const Color(0xFFE07A5F), 12)),
                          Positioned(top: 30, right: 15, child: _buildPixelBlock(const Color(0xFF81B29A), 18, opacity: 0.6)),
                          Positioned(bottom: 10, left: 35, child: _buildPixelBlock(const Color(0xFFF2CC8F), 22)),
                          Positioned(bottom: 25, right: 30, child: _buildPixelBlock(const Color(0xFF3D405B), 14, opacity: 0.8)),
                          
                          // 中间的两位小动物！
                          Positioned(
                            left: 25,
                            bottom: 30,
                            child: PixelMascot(type: mascot1, action: MascotAction.happy, size: 45),
                          ),
                          Positioned(
                            right: 25,
                            bottom: 30,
                            child: PixelMascot(type: mascot2, action: MascotAction.happy, size: 45),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    
                    // 2. 标题排版
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