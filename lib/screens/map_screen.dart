import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import '../widgets/pixel_mascot.dart';
import 'event_detail_screen.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  final Set<String> _clearedEventIds = {'e1', 'e5'};
  TourismEvent? _selectedEvent;
  String _currentLocationId = 'e5';

  static const Map<String, Offset> _relativeCoords = {
    'e1': Offset(0.19, 0.23), // Penang
    'e3': Offset(0.34, 0.70), // Melaka
    'e5': Offset(0.41, 0.82), // Johor
    'e2': Offset(0.48, 0.72), // Sarawak (Kuching)
    'e4': Offset(0.79, 0.32), // Sabah (KK)
  };

  void _unlockEvent(String id) {
    setState(() {
      _clearedEventIds.add(id);
      _currentLocationId = id; 
      _selectedEvent = MockEventRepository.events.firstWhere((e) => e.id == id);
    });
  }

  @override
  Widget build(BuildContext context) {
    final allEvents = MockEventRepository.events;
    final total = allEvents.length;
    final cleared = _clearedEventIds.length;
    final percentage = (cleared / total * 100).toInt();

    return Scaffold(
      backgroundColor: const Color(0xFF060B13),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0B1322),
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.explore, color: Color(0xFF00FF9D), size: 20),
            SizedBox(width: 8),
            Text(
              'Batik Heritage Map',
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
                  color: const Color(0xFF00FF9D).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF00FF9D)),
                ),
                child: Text(
                  '$percentage% Explored',
                  style: const TextStyle(color: Color(0xFF00FF9D), fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ),
        ],
      ),
      body: Stack(
        children: [
          InteractiveViewer(
            boundaryMargin: const EdgeInsets.all(40),
            minScale: 0.8,
            maxScale: 3.0,
            child: Center(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: AspectRatio(
                  aspectRatio: 16 / 9, 
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final mapW = constraints.maxWidth;
                      final mapH = constraints.maxHeight;

                      return Stack(
                        clipBehavior: Clip.none,
                        fit: StackFit.expand,
                        children: [
                          Image.asset(
                            'assets/images/batik_msia_map.png',
                            fit: BoxFit.contain,
                            errorBuilder: (context, error, stackTrace) => Container(
                              color: const Color(0xFF0F172A),
                              alignment: Alignment.center,
                              child: const Text(
                                'Please place batik_msia_map.png in assets/images/',
                                style: TextStyle(color: Colors.white60, fontSize: 12),
                              ),
                            ),
                          ),

                          ...allEvents.map((event) {
                            final rel = _relativeCoords[event.id] ?? const Offset(0.5, 0.5);
                            final isCleared = _clearedEventIds.contains(event.id);

                            final posX = rel.dx * mapW;
                            final posY = rel.dy * mapH;

                            return Positioned(
                              left: posX - 16,
                              top: posY - 16,
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
                                      width: 32,
                                      height: 32,
                                      decoration: BoxDecoration(
                                        color: isCleared ? const Color(0xFF00FF9D) : const Color(0xFF1E293B),
                                        shape: BoxShape.circle,
                                        border: Border.all(
                                          color: isCleared ? Colors.white : Colors.white54,
                                          width: 2,
                                        ),
                                        boxShadow: [
                                          BoxShadow(
                                            color: (isCleared ? const Color(0xFF00FF9D) : Colors.black).withOpacity(0.5),
                                            blurRadius: 8,
                                          ),
                                        ],
                                      ),
                                      child: Icon(
                                        isCleared ? Icons.location_on : Icons.lock,
                                        color: isCleared ? const Color(0xFF060B13) : Colors.white70,
                                        size: 16,
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                                      decoration: BoxDecoration(
                                        color: Colors.black.withOpacity(0.75),
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Text(
                                        event.state,
                                        style: TextStyle(
                                          color: isCleared ? const Color(0xFF00FF9D) : Colors.white60,
                                          fontSize: 9,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          }),

                          ValueListenableBuilder<MascotType>(
                            valueListenable: UserSettings.instance.selectedMascot,
                            builder: (context, currentMascot, _) {
                              final rel = _relativeCoords[_currentLocationId] ?? const Offset(0.5, 0.5);
                              final posX = rel.dx * mapW;
                              final posY = rel.dy * mapH;

                              return Positioned(
                                left: posX - 18,
                                top: posY - 48, 
                                child: Column(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF060B13),
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(color: const Color(0xFF00FF9D), width: 1),
                                      ),
                                      child: const Text(
                                        'You are here',
                                        style: TextStyle(
                                          color: Color(0xFF00FF9D),
                                          fontSize: 8,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 2),
                                    PixelMascot(
                                      type: currentMascot,
                                      action: MascotAction.idleFront,
                                      size: 36,
                                    ),
                                  ],
                                ),
                              );
                            },
                          ),
                        ],
                      );
                    },
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
                      color: const Color(0xFF0F1A2A),
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(
                        color: _clearedEventIds.contains(_selectedEvent!.id)
                            ? const Color(0xFF00FF9D)
                            : Colors.white24,
                      ),
                      boxShadow: [
                        BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 16),
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
                                      color: Color(0xFF00FF9D),
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
                                    backgroundColor: const Color(0xFF00FF9D),
                                    foregroundColor: const Color(0xFF060B13),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                  ),
                                  icon: const Icon(Icons.lock_open, size: 16),
                                  label: const Text('Unlock Location (Travel Here)', style: TextStyle(fontWeight: FontWeight.bold)),
                                  onPressed: () => _unlockEvent(_selectedEvent!.id),
                                )
                              : OutlinedButton(
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFF00FF9D)),
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
                                  child: const Text('View Experience Details', style: TextStyle(color: Color(0xFF00FF9D))),
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
}