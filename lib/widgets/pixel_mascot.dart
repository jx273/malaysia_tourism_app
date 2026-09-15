import 'dart:async';
import 'package:flutter/material.dart';

enum MascotType { tapir, tiger }

enum MascotAction {
  idleFront(0),
  idleBack(1),
  walkDown(2),
  walkUp(3),
  walkLeft(4),
  walkRight(5),
  peek(6),
  textboxPeek(7),
  yawn(8),
  confused(9),
  happy(10),
  coverEyes(11);

  final int rowIndex;
  const MascotAction(this.rowIndex);
}

class PixelMascot extends StatefulWidget {
  final MascotType type;
  final MascotAction action;
  final double size;
  final bool animate;

  const PixelMascot({
    super.key,
    this.type = MascotType.tiger,
    this.action = MascotAction.idleFront,
    this.size = 54,
    this.animate = true,
  });

  @override
  State<PixelMascot> createState() => _PixelMascotState();
}

class _PixelMascotState extends State<PixelMascot> {
  int _currentFrame = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    if (widget.animate) {
      _timer = Timer.periodic(const Duration(milliseconds: 180), (timer) {
        if (mounted) {
          setState(() {
            _currentFrame = (_currentFrame + 1) % 4;
          });
        }
      });
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final assetPath = widget.type == MascotType.tapir
        ? 'assets/images/tapir_sheet.png'
        : 'assets/images/tiger_sheet.png';

    final scale = widget.size / 64.0;

    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: ClipRect(
        child: OverflowBox(
          alignment: Alignment.topLeft,
          minWidth: 256 * scale,
          maxWidth: 256 * scale,
          minHeight: 768 * scale,
          maxHeight: 768 * scale,
          child: Transform.translate(
            offset: Offset(
              -_currentFrame * 64.0 * scale,
              -widget.action.rowIndex * 64.0 * scale,
            ),
            child: Image.asset(
              assetPath,
              filterQuality: FilterQuality.none,
            ),
          ),
        ),
      ),
    );
  }
}