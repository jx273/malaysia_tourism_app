import 'dart:io';
import 'dart:ui' as ui;
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:share_plus/share_plus.dart';
import '../data/passport_repository.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import '../widgets/pixel_mascot.dart';

class PassportScreen extends StatelessWidget {
  const PassportScreen({super.key});

  Widget _staticMascotSticker(MascotType type) {
    final assetPath = type == MascotType.tapir ? 'assets/images/tapir_sheet.png' : 'assets/images/tiger_sheet.png';
    const scale = 50.0 / 64.0;
    return SizedBox(
      width: 50, height: 50,
      child: ClipRect(
        child: OverflowBox(
          alignment: Alignment.topLeft,
          minWidth: 256.0 * scale, maxWidth: 256.0 * scale,
          minHeight: 768.0 * scale, maxHeight: 768.0 * scale,
          child: Image.asset(assetPath, filterQuality: FilterQuality.none),
        ),
      ),
    );
  }

  void _showEnlargedPostcard(BuildContext context, PostcardMemory mem) {
    final timeString = TimeOfDay.fromDateTime(mem.checkInTime).format(context);
    final dateString = '${mem.checkInTime.day.toString().padLeft(2, '0')}/${mem.checkInTime.month.toString().padLeft(2, '0')}/${mem.checkInTime.year}';
    final GlobalKey boundaryKey = GlobalKey(); 

    showGeneralDialog(
      context: context,
      barrierDismissible: true,
      barrierLabel: 'Close',
      barrierColor: Colors.black.withValues(alpha: 0.5),
      transitionDuration: const Duration(milliseconds: 400),
      pageBuilder: (context, anim1, anim2) => Container(),
      transitionBuilder: (context, anim1, anim2, child) {
        final curve = CurvedAnimation(parent: anim1, curve: Curves.easeOutBack);
        return ScaleTransition(
          scale: Tween<double>(begin: 0.8, end: 1.0).animate(curve),
          child: FadeTransition(
            opacity: anim1,
            child: AlertDialog(
              backgroundColor: const Color(0xFFF4F1DE),
              contentPadding: const EdgeInsets.all(16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  RepaintBoundary(
                    key: boundaryKey,
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.12), blurRadius: 12, offset: const Offset(0, 4))],
                      ),
                      child: Column(
                        children: [
                          AspectRatio(
                            aspectRatio: 3 / 4,
                            child: Stack(
                              fit: StackFit.expand,
                              children: [
                                ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: mem.userPhotoUrl.startsWith('http') 
                                      ? Image.network(mem.userPhotoUrl, fit: BoxFit.cover)
                                      : Image.file(File(mem.userPhotoUrl), fit: BoxFit.cover),
                                ),
                                Positioned(
                                  top: 12, right: 12,
                                  child: Text(
                                    '$dateString $timeString',
                                    style: const TextStyle(color: Color(0xFFE07A5F), fontSize: 7, fontWeight: FontWeight.w900, shadows: [Shadow(color: Colors.white, blurRadius: 3)]),
                                  ),
                                ),
                                Positioned(
                                  bottom: 12, left: 12,
                                  child: ValueListenableBuilder<MascotType>(
                                    valueListenable: UserSettings.instance.selectedMascot,
                                    builder: (_, m, _) => _staticMascotSticker(m),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 16),
                          Text(
                            mem.event.title, 
                            textAlign: TextAlign.center, 
                            style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 12, color: Color(0xFF3D405B))
                          ),
                          const SizedBox(height: 12),
                          Text(
                            mem.note.isEmpty ? '' : '"${mem.note}"',
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 10, fontStyle: FontStyle.italic, color: Color(0xFFE07A5F), fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      TextButton(onPressed: () => Navigator.pop(context), child: const Text('Close', style: TextStyle(color: Colors.grey))),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF3D405B), foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16))),
                        icon: const Icon(Icons.share, size: 16),
                        label: const Text('Share Story'),
                        onPressed: () async {
                          final textToShare = 'Check out my visit to ${mem.event.title}! "${mem.note}"';
                          try {
                            RenderRepaintBoundary boundary = boundaryKey.currentContext!.findRenderObject() as RenderRepaintBoundary;
                            ui.Image image = await boundary.toImage(pixelRatio: 3.0);
                            ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
                            if (byteData != null) {
                              final file = File('${Directory.systemTemp.path}/share_mem.png');
                              await file.writeAsBytes(byteData.buffer.asUint8List());
                              await Share.shareXFiles([XFile(file.path)], text: textToShare);
                            }
                          } catch (e) {
                            Share.share(textToShare);
                          }
                        },
                      ),
                    ],
                  )
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      appBar: AppBar(
        backgroundColor: const Color(0xFFF4F1DE),
        elevation: 0,
        title: const Text('Passport ✈️', style: TextStyle(color: Color(0xFF3D405B), fontWeight: FontWeight.w900, fontSize: 22)),
      ),
      body: ValueListenableBuilder<List<PostcardMemory>>(
        valueListenable: PassportRepository.instance.memories,
        builder: (context, memories, _) {
          
          if (memories.isEmpty) {
            return CustomPaint(
              painter: _PatternPainter(), 
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.photo_album_outlined, size: 60, color: Color(0xFF81B29A)),
                    const SizedBox(height: 16),
                    const Text('Your Passport is empty', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: Color(0xFF3D405B))),
                    const SizedBox(height: 8),
                    Text('Visit locations and snap postcards\nto fill up your journey.', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
                  ],
                ),
              ),
            );
          }

          return CustomPaint(
            painter: _PatternPainter(), 
            child: Center( 
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 600), 
                child: CustomScrollView(
                  physics: const BouncingScrollPhysics(),
                  slivers: [
                    SliverPadding(
                      padding: const EdgeInsets.fromLTRB(20, 10, 20, 20),
                      sliver: SliverGrid(
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 16,
                          mainAxisSpacing: 16,
                          childAspectRatio: 0.72, 
                        ),
                        delegate: SliverChildBuilderDelegate(
                          (context, i) {
                            final mem = memories[i];
                            return GestureDetector(
                              onTap: () => _showEnlargedPostcard(context, mem),
                              child: Container(
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(12),
                                  boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.08), blurRadius: 10, offset: const Offset(0, 4))],
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.stretch,
                                  children: [
                                    Expanded(
                                      child: Padding(
                                        padding: const EdgeInsets.all(8.0),
                                        child: Stack(
                                          fit: StackFit.expand,
                                          children: [
                                            ClipRRect(
                                              borderRadius: BorderRadius.circular(6),
                                              child: mem.userPhotoUrl.startsWith('http') 
                                                  ? Image.network(mem.userPhotoUrl, fit: BoxFit.cover)
                                                  : Image.file(File(mem.userPhotoUrl), fit: BoxFit.cover),
                                            ),
                                            Positioned(
                                              bottom: 4, left: 4,
                                              child: ValueListenableBuilder<MascotType>(
                                                valueListenable: UserSettings.instance.selectedMascot,
                                                builder: (_, m, _) => Transform.scale(scale: 0.8, child: _staticMascotSticker(m)),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                                      child: Text(
                                        mem.event.title,
                                        maxLines: 3,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 8, color: Color(0xFF3D405B)),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                          childCount: memories.length,
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.only(top: 20, bottom: 120, left: 40, right: 40),
                        child: Column(
                          children: [
                            Divider(color: Colors.grey.shade300, thickness: 1),
                            const SizedBox(height: 12),
                            Text(
                              "Keep exploring to expand your journey...",
                              style: TextStyle(color: Colors.grey.shade500, fontStyle: FontStyle.italic, fontSize: 12, fontWeight: FontWeight.w600),
                            ),
                          ],
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

class _PatternPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0xFF3D405B).withValues(alpha: 0.07);
    const spacing = 30.0;
    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        final offsetX = (y / spacing) % 2 == 0 ? x : x + spacing / 2;
        canvas.drawCircle(Offset(offsetX, y), 2, paint);
      }
    }
  }
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}