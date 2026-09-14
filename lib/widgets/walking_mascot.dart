import 'package:flutter/material.dart';
import 'pixel_mascot.dart';
import '../data/mock_events.dart';

class WalkingMascot extends StatefulWidget {
  final VoidCallback onTap;

  const WalkingMascot({super.key, required this.onTap});

  @override
  State<WalkingMascot> createState() => _WalkingMascotState();
}

class _WalkingMascotState extends State<WalkingMascot> {
  bool _movingRight = true;
  double _xOffset = 20.0;

  @override
  void initState() {
    super.initState();
    _startPatrol();
  }

  void _startPatrol() async {
    while (mounted) {
      await Future.delayed(const Duration(milliseconds: 3200));
      if (!mounted) return;
      setState(() {
        _movingRight = !_movingRight;
        _xOffset = _movingRight ? 180.0 : 20.0;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<MascotType>(
      valueListenable: MascotSettings.instance.currentMascot,
      builder: (context, mascotType, child) {
        return AnimatedPositioned(
          duration: const Duration(milliseconds: 3000),
          curve: Curves.easeInOut,
          left: _xOffset,
          bottom: 12,
          child: GestureDetector(
            onTap: widget.onTap,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF007A3D), width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.08),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.auto_awesome, color: Color(0xFF007A3D), size: 12),
                      const SizedBox(width: 4),
                      Text(
                        mascotType == MascotType.tapir ? 'Ask Ollie (Tapir)!' : 'Ask Leo (Tiger)!',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 4),
                PixelMascot(
                  type: mascotType,
                  action: _movingRight ? MascotAction.walkRight : MascotAction.walkLeft,
                  size: 58,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}