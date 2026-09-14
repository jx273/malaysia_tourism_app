import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../models/tourism_event.dart';
import 'event_detail_screen.dart';
import '../widgets/pixel_mascot.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final Set<String> _clearedEventIds = {'e1'};
  TourismEvent? _selectedEvent;

  void _dispelFog(String id) {
    setState(() {
      _clearedEventIds.add(id);
      _selectedEvent = MockEventRepository.events.firstWhere((e) => e.id == id);
    });
  }

  @override
  Widget build(BuildContext context) {
    final allEvents = MockEventRepository.events;
    final total = allEvents.length;
    final cleared = _clearedEventIds.length;
    final percentage = (cleared / total * 100).toInt();

    const mapWidth = 380.0;
    const mapHeight = 320.0;

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.radar, color: Color(0xFF34D399), size: 20),
            SizedBox(width: 8),
            Text(
              'Fog of Discovery',
              style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ],
        ),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF34D399).withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF34D399)),
                ),
                child: Text(
                  '$percentage% Unlocked',
                  style: const TextStyle(color: Color(0xFF34D399), fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          InteractiveViewer(
            boundaryMargin: const EdgeInsets.all(30),
            minScale: 0.8,
            maxScale: 2.5,
            child: Center(
              child: Container(
                width: mapWidth,
                height: mapHeight,
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white12),
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      Image.network(
                        'https://raw.githubusercontent.com/djaiss/mapsicon/master/all/my/vector.svg.png',
                        fit: BoxFit.contain,
                        color: const Color(0xFF334155), 
                        colorBlendMode: BlendMode.srcIn,
                        errorBuilder: (context, error, stackTrace) => Container(
                          color: const Color(0xFF1E293B),
                          alignment: Alignment.center,
                          child: const Text('Map Loading...', style: TextStyle(color: Colors.white38)),
                        ),
                      ),

                      CustomPaint(
                        size: const Size(mapWidth, mapHeight),
                        painter: FogMaskPainter(
                          allEvents: allEvents,
                          clearedIds: _clearedEventIds,
                        ),
                      ),

                      ...allEvents.map((event) {
                        final isCleared = _clearedEventIds.contains(event.id);
                        final offset = _getMapCoordinates(event.id);

                        return Positioned(
                          left: offset.dx - 18,
                          top: offset.dy - 18,
                          child: GestureDetector(
                            onTap: () {
                              setState(() {
                                _selectedEvent = event;
                              });
                            },
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 36,
                                  height: 36,
                                  decoration: BoxDecoration(
                                    color: isCleared ? const Color(0xFF007A3D) : const Color(0xFF475569),
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                      color: isCleared ? const Color(0xFF34D399) : Colors.white60,
                                      width: 2,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color: (isCleared ? const Color(0xFF34D399) : Colors.black).withValues(alpha: 0.5),
                                        blurRadius: 8,
                                      ),
                                    ],
                                  ),
                                  child: Icon(
                                    isCleared ? Icons.place : Icons.lock,
                                    color: isCleared ? Colors.white : Colors.white70,
                                    size: 18,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                                  decoration: BoxDecoration(
                                    color: Colors.black.withValues(alpha: 0.7),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    isCleared ? event.state : '???',
                                    style: TextStyle(
                                      color: isCleared ? const Color(0xFF34D399) : Colors.white60,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                      Builder(
                        builder: (context) {
                          const recentId = 'e1'; 
                          final coord = _getMapCoordinates(recentId);
                          return Positioned(
                            left: coord.dx - 20,
                            top: coord.dy - 44, 
                            child: const Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  '📍 You were here',
                                  style: TextStyle(
                                    color: Color(0xFF34D399),
                                    fontSize: 9,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                PixelMascot(
                                  type: MascotType.tapir,
                                  action: MascotAction.idleFront, 
                                  size: 34,
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          if (_selectedEvent != null)
            Positioned(
              bottom: 20,
              left: 20,
              right: 20,
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 480),
                  child: Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(
                        color: _clearedEventIds.contains(_selectedEvent!.id)
                            ? const Color(0xFF34D399)
                            : Colors.white24,
                      ),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withValues(alpha: 0.5), blurRadius: 16),
                      ],
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Row(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(10),
                              child: Image.network(
                                _selectedEvent!.imageUrl,
                                width: 50,
                                height: 50,
                                fit: BoxFit.cover,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _selectedEvent!.state,
                                    style: const TextStyle(
                                      color: Color(0xFF34D399),
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Text(
                                    _selectedEvent!.title,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.close, color: Colors.white54, size: 20),
                              onPressed: () => setState(() => _selectedEvent = null),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: !_clearedEventIds.contains(_selectedEvent!.id)
                              ? ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF34D399),
                                    foregroundColor: const Color(0xFF0F172A),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                  icon: const Icon(Icons.flash_on, size: 16),
                                  label: const Text('Dispel Fog (Unlock)', style: TextStyle(fontWeight: FontWeight.bold)),
                                  onPressed: () => _dispelFog(_selectedEvent!.id),
                                )
                              : OutlinedButton(
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFF34D399)),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                  onPressed: () {
                                    Navigator.push(
                                      context,
                                      MaterialPageRoute(
                                        builder: (context) => EventDetailScreen(event: _selectedEvent!),
                                      ),
                                    );
                                  },
                                  child: const Text('View Destination Details', style: TextStyle(color: Color(0xFF34D399))),
                                ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  static Offset _getMapCoordinates(String id) {
    switch (id) {
      case 'e1': 
        return const Offset(42, 115);
      case 'e3': 
        return const Offset(75, 185);
      case 'e2': 
        return const Offset(205, 235);
      case 'e4': 
        return const Offset(335, 120);
      default:
        return const Offset(100, 100);
    }
  }
}

class FogMaskPainter extends CustomPainter {
  final List<TourismEvent> allEvents;
  final Set<String> clearedIds;

  FogMaskPainter({required this.allEvents, required this.clearedIds});

  @override
  void paint(Canvas canvas, Size size) {
    canvas.saveLayer(Rect.fromLTWH(0, 0, size.width, size.height), Paint());

    final fogPaint = Paint()
      ..color = const Color(0xFF0F172A).withValues(alpha: 0.85)
      ..style = PaintingStyle.fill;
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), fogPaint);

    final clearPaint = Paint()
      ..blendMode = BlendMode.clear
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 28);

    for (final event in allEvents) {
      if (clearedIds.contains(event.id)) {
        final center = _MapScreenState._getMapCoordinates(event.id);
        canvas.drawCircle(center, 42, clearPaint);
      }
    }

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant FogMaskPainter oldDelegate) => true;
}