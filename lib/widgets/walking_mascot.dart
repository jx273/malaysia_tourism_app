import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import 'pixel_mascot.dart';

class WalkingMascot extends StatefulWidget {
  final VoidCallback onTap;
  const WalkingMascot({super.key, required this.onTap});

  @override
  State<WalkingMascot> createState() => _WalkingMascotState();
}

class _WalkingMascotState extends State<WalkingMascot> {
  // Default position is at the bottom right corner of the screen
  double _x = 300.0; 
  double _y = 100.0;
  
  bool _isDragging = false;
  bool _isResting = true; 
  bool _movingRight = false; 
  int _textIndex = 0;
  Timer? _behaviorTimer;
  final Random _rnd = Random();

  final List<String> _phrases = [
    'Tap to chat! ✨',
    'Find eco trails 🌿',
    'Hungry? Ask me! 🍜',
    'Check my tips! 🗺️'
  ];

  @override
  void initState() {
    super.initState();
    // Set the initial position to the right side of the screen after the first frame is rendered
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        setState(() {
          _x = MediaQuery.of(context).size.width - 80;
        });
      }
    });
    _startBehaviorLoop();
  }

  @override
  void dispose() {
    _behaviorTimer?.cancel();
    super.dispose();
  }

  // Every 5 seconds, randomly decide to either rest or walk in a random direction
  void _startBehaviorLoop() {
    _behaviorTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (!mounted || _isDragging) return;

      setState(() {
        _textIndex = (_textIndex + 1) % _phrases.length;
        
        // 70% chance to rest, 30% chance to walk
        if (_rnd.nextDouble() > 0.3) {
          _isResting = true;
        } else {
          _isResting = false;
          _movingRight = _rnd.nextBool();
          
          final screenW = MediaQuery.of(context).size.width;
          
          // Ensure that the mascot moves at least 50 pixels and at most 120 pixels in one go, avoiding standing still
          double moveDelta = _rnd.nextDouble() * 70 + 50; 
          
          if (_movingRight) {
            _x += moveDelta;
            // If the mascot moves beyond the right edge, set it to the maximum allowed position and change direction
            if (_x > screenW - 80) {
              _x = screenW - 80;
              _movingRight = false;
            }
          } else {
            _x -= moveDelta;
            // If the mascot moves beyond the left edge, set it to the minimum allowed position and change direction
            if (_x < 20) {
              _x = 20;
              _movingRight = true;
            }
          }
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final screenW = MediaQuery.of(context).size.width;
    final screenH = MediaQuery.of(context).size.height;

    return ValueListenableBuilder<MascotType>(
      valueListenable: UserSettings.instance.selectedMascot,
      builder: (context, currentMascot, _) {
        MascotAction action;
        if (_isDragging) {
          action = MascotAction.confused;
        } else if (_isResting) {
          action = MascotAction.idleFront;
        } else {
          action = _movingRight ? MascotAction.walkRight : MascotAction.walkLeft;
        }

        return AnimatedPositioned(
          duration: _isDragging ? Duration.zero : const Duration(milliseconds: 4500),
          curve: Curves.easeInOut,
          left: _x,
          bottom: _y,
          child: GestureDetector(
            onTap: widget.onTap,
            onPanStart: (_) => setState(() => _isDragging = true),
            onPanUpdate: (details) {
              setState(() {
                _x = (_x + details.delta.dx).clamp(10.0, screenW - 70.0);
                _y = (_y - details.delta.dy).clamp(80.0, screenH - 150.0);
              });
            },
            onPanEnd: (_) => setState(() => _isDragging = false),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center, 
              children: [
                if (!_isDragging)
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 400),
                    child: Container(
                      key: ValueKey<int>(_textIndex),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.9),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFE07A5F), width: 1.5),
                      ),
                      child: Text(
                        _phrases[_textIndex],
                        style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF3D405B)),
                      ),
                    ),
                  ),
                const SizedBox(height: 4),
                PixelMascot(type: currentMascot, action: action, size: 60),
              ],
            ),
          ),
        );
      },
    );
  }
}