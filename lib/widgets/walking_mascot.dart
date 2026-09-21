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
  // Use nullable to avoid hardcoded off-screen starting position
  double? _x; 
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
    _startBehaviorLoop();
  }

  @override
  void dispose() {
    _behaviorTimer?.cancel();
    super.dispose();
  }

  void _startBehaviorLoop() {
    _behaviorTimer = Timer.periodic(const Duration(seconds: 5), (timer) {
      if (!mounted || _isDragging || _x == null) return;

      setState(() {
        _textIndex = (_textIndex + 1) % _phrases.length;
        
        if (_rnd.nextDouble() > 0.3) {
          _isResting = true;
        } else {
          _isResting = false;
          _movingRight = _rnd.nextBool();
          
          final screenW = MediaQuery.of(context).size.width;
          double moveDelta = _rnd.nextDouble() * 70 + 50; 
          
          if (_movingRight) {
            _x = (_x! + moveDelta);
            // Increased right-side margin to prevent speech bubble cutoff
            if (_x! > screenW - 140.0) {
              _x = screenW - 140.0;
              _movingRight = false;
            }
          } else {
            _x = (_x! - moveDelta);
            if (_x! < 20) {
              _x = 20.0;
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

    // Start mascot at its intended final position safely
    _x ??= screenW - 140.0; 
    
    // Constrain X and Y bounds permanently against screen resizes
    _x = _x!.clamp(10.0, screenW - 140.0);
    _y = _y.clamp(80.0, screenH - 150.0);

    return ValueListenableBuilder<MascotType>(
      valueListenable: UserSettings.instance.selectedMascot,
      builder: (context, currentMascot, _) {
        MascotAction action;
        if (_isDragging) {
          action = MascotAction.confused;
        } else if (_isResting) {
          action = MascotAction.idleFront;
        } else {
          // Play walk animation naturally following X translation
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
                _x = (_x! + details.delta.dx).clamp(10.0, screenW - 140.0);
                _y = (_y - details.delta.dy).clamp(80.0, screenH - 150.0);
              });
            },
            onPanEnd: (_) => setState(() {
              _isDragging = false;
              _isResting = true; // Return to idle sprite when dropped
            }),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center, 
              children: [
                if (!_isDragging)
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 400),
                    child: Container(
                      key: ValueKey<int>(_textIndex),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.95),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFE07A5F), width: 1.5),
                        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 4, offset: const Offset(0, 2))],
                      ),
                      child: Text(
                        _phrases[_textIndex],
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF3D405B)),
                      ),
                    ),
                  ),
                const SizedBox(height: 6),
                PixelMascot(type: currentMascot, action: action, size: 64),
              ],
            ),
          ),
        );
      },
    );
  }
}