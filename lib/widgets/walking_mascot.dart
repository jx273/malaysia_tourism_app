import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import 'pixel_mascot.dart';

class WalkingMascot extends StatefulWidget {
  final VoidCallback onTap;
  final String speechText;

  const WalkingMascot({
    super.key,
    required this.onTap,
    this.speechText = 'Ask AI Guide!',
  });

  @override
  State<WalkingMascot> createState() => _WalkingMascotState();
}

class _WalkingMascotState extends State<WalkingMascot> {
  double _x = 24.0;
  double _y = 0.0;
  bool _isDragging = false;
  bool _movingRight = true;

  @override
  void initState() {
    super.initState();
    _startAutoWalk();
  }

  void _startAutoWalk() async {
    while (mounted) {
      await Future.delayed(const Duration(milliseconds: 3200));
      if (!mounted) return;
      if (!_isDragging) {
        setState(() {
          _movingRight = !_movingRight;
          _x = _movingRight ? 200.0 : 24.0;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<MascotType>(
      valueListenable: UserSettings.instance.selectedMascot,
      builder: (context, currentMascot, _) {
        final action = _isDragging
            ? MascotAction.confused
            : (_movingRight ? MascotAction.walkRight : MascotAction.walkLeft);

        return AnimatedPositioned(
          duration: _isDragging ? Duration.zero : const Duration(milliseconds: 3000),
          curve: Curves.easeInOut,
          left: _x,
          bottom: 16 - _y,
          child: GestureDetector(
            onTap: widget.onTap,
            onPanStart: (_) {
              setState(() {
                _isDragging = true;
              });
            },
            onPanUpdate: (details) {
              setState(() {
                _x += details.delta.dx;
                _y -= details.delta.dy;
              });
            },
            onPanEnd: (_) {
              setState(() {
                _isDragging = false;
                if (_y < -20 || _y > 100) {
                  _y = 0; 
                }
              });
            },
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (!_isDragging)
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
                          widget.speechText,
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
                  type: currentMascot,
                  action: action,
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