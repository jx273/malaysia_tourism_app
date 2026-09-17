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
  // 默认停在右下角安全位置
  double _x = 300.0; 
  double _y = 100.0;
  
  bool _isDragging = false;
  bool _isResting = true; // 默认休息状态
  bool _movingRight = false; // 默认面向左边
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
    // 初始设置一个靠右的位置 (等待第一次 build 后如果有屏幕宽度再修正)
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

  // 走一下，休息一下的逻辑
  void _startBehaviorLoop() {
    _behaviorTimer = Timer.periodic(const Duration(seconds: 4), (timer) {
      if (!mounted || _isDragging) return;

      setState(() {
        _textIndex = (_textIndex + 1) % _phrases.length;
        
        // 60% 概率休息，40% 概率走动
        if (_rnd.nextDouble() > 0.4) {
          _isResting = true;
        } else {
          _isResting = false;
          _movingRight = _rnd.nextBool();
          
          final screenW = MediaQuery.of(context).size.width;
          
          // 确保单次至少走 50 像素，最多走 120 像素，拒绝原地踏步
          double moveDelta = _rnd.nextDouble() * 70 + 50; 
          
          if (_movingRight) {
            _x += moveDelta;
            // 碰到右边缘就强行回头
            if (_x > screenW - 80) {
              _x = screenW - 80;
              _movingRight = false;
            }
          } else {
            _x -= moveDelta;
            // 碰到左边缘就强行回头
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
          duration: _isDragging ? Duration.zero : const Duration(milliseconds: 2500),
          curve: Curves.easeInOut,
          left: _x,
          bottom: _y,
          child: GestureDetector(
            onTap: widget.onTap,
            onPanStart: (_) => setState(() => _isDragging = true),
            onPanUpdate: (details) {
              setState(() {
                // 修复：全向自由拖动 (X 和 Y 同时响应增量)
                _x = (_x + details.delta.dx).clamp(10.0, screenW - 70.0);
                _y = (_y - details.delta.dy).clamp(80.0, screenH - 150.0);
              });
            },
            onPanEnd: (_) => setState(() => _isDragging = false),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center, // 居中对齐文字气泡和动物
              children: [
                if (!_isDragging)
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 400),
                    child: Container(
                      key: ValueKey<int>(_textIndex),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
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