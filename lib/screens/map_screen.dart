import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
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

class _MapScreenState extends State<MapScreen> with TickerProviderStateMixin {
  final MapController _mapController = MapController();
  TourismEvent? _selectedEvent;
  
  final LatLng _malaysiaCenter = const LatLng(4.0, 109.0);
  final double _defaultZoom = 5.0;

  final ColorFilter _mapThemeFilter = const ColorFilter.matrix([
    0.85, 0.1,  0.0,  0, 25, 
    0.1,  0.85, 0.1,  0, 30, 
    0.1,  0.1,  0.75, 0, 15, 
    0,    0,    0,    1, 0,  
  ]);

  final EdgeInsets _mapFitPadding = const EdgeInsets.only(left: 50.0, right: 50.0, top: 160.0, bottom: 220.0);

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  LatLngBounds? _getEventBounds() {
    final events = MockEventRepository.events;
    if (events.isEmpty) return null;
    
    final points = events.map((e) => LatLng(e.latitude, e.longitude)).toList();
    return LatLngBounds.fromPoints(points);
  }

  void _animatedMapMove(LatLng destLocation, double destZoom) {
    final controller = AnimationController(
      vsync: this, 
      duration: const Duration(milliseconds: 600)
    );
    
    final latTween = Tween<double>(begin: _mapController.camera.center.latitude, end: destLocation.latitude);
    final lngTween = Tween<double>(begin: _mapController.camera.center.longitude, end: destLocation.longitude);
    final zoomTween = Tween<double>(begin: _mapController.camera.zoom, end: destZoom);

    final Animation<double> animation = CurvedAnimation(parent: controller, curve: Curves.easeOutCubic);

    controller.addListener(() {
      _mapController.move(
        LatLng(latTween.evaluate(animation), lngTween.evaluate(animation)),
        zoomTween.evaluate(animation),
      );
    });

    animation.addStatusListener((status) {
      if (status == AnimationStatus.completed || status == AnimationStatus.dismissed) {
        controller.dispose();
      }
    });

    controller.forward();
  }

  void _zoomIn() {
    final currentZoom = _mapController.camera.zoom;
    if (currentZoom >= 17.5) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reached maximum zoom! 🐯🔍'), duration: Duration(seconds: 1)),
      );
      return;
    }
    _animatedMapMove(_mapController.camera.center, currentZoom + 1.2);
  }

  void _zoomOut() {
    final currentZoom = _mapController.camera.zoom;
    if (currentZoom <= 5.0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reached minimum zoom! 🗺️'), duration: Duration(seconds: 1)),
      );
      return;
    }
    _animatedMapMove(_mapController.camera.center, currentZoom - 1.2);
  }

  @override
  Widget build(BuildContext context) {
    final events = MockEventRepository.events;
    final bounds = _getEventBounds();

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      body: Stack(
        children: [
          // 1. Base Map Layer
          ColorFiltered(
            colorFilter: _mapThemeFilter,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCameraFit: bounds != null 
                    ? CameraFit.bounds(bounds: bounds, padding: _mapFitPadding, maxZoom: 10.0)
                    : null,
                initialCenter: bounds == null ? _malaysiaCenter : const LatLng(0, 0),
                initialZoom: bounds == null ? _defaultZoom : 0,
                minZoom: 4.5,
                maxZoom: 18,
                onTap: (_, _) => setState(() => _selectedEvent = null),
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.example.malaysia_tourism_app',
                ),
                MarkerLayer(
                  markers: events.map((ev) {
                    final isSel = _selectedEvent?.id == ev.id;
                    final eventLocation = LatLng(ev.latitude, ev.longitude);

                    return Marker(
                      point: eventLocation,
                      width: 50, 
                      height: 50,
                      child: Center(
                        child: GestureDetector(
                          behavior: HitTestBehavior.deferToChild,
                          onTap: () {
                            setState(() => _selectedEvent = ev);
                            _animatedMapMove(eventLocation, 13.0); 
                          },
                          child: AnimatedScale(
                            scale: isSel ? 1.35 : 1.0,
                            duration: const Duration(milliseconds: 400),
                            curve: Curves.elasticOut,
                            child: Container(
                              padding: const EdgeInsets.all(3),
                              decoration: BoxDecoration(
                                color: isSel ? const Color(0xFFE07A5F) : Colors.white,
                                shape: BoxShape.circle,
                                border: Border.all(color: isSel ? Colors.white : const Color(0xFF81B29A), width: 2.0),
                                boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.25), blurRadius: 8, offset: const Offset(0, 3))],
                              ),
                              child: ValueListenableBuilder<MascotType>(
                                valueListenable: UserSettings.instance.selectedMascot,
                                builder: (_, mascotType, _) => PixelMascot(
                                  type: mascotType,
                                  action: isSel ? MascotAction.happy : MascotAction.idleFront,
                                  size: 28, 
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),

          // 2. Top Title Bar (Ghost Gradient + Button Penetration)
          Positioned(
            top: 0, left: 0, right: 0,
            child: Stack(
              children: [
                IgnorePointer(
                  child: Container(
                    height: 140, 
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          const Color(0xFFF4F1DE).withValues(alpha: 1.0),
                          const Color(0xFFF4F1DE).withValues(alpha: 0.8),
                          const Color(0xFFF4F1DE).withValues(alpha: 0.0),
                        ],
                      ),
                    ),
                  ),
                ),
                SafeArea(
                  bottom: false,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    child: Row(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.85), shape: BoxShape.circle),
                          child: const Icon(Icons.explore, color: Color(0xFF3D405B), size: 20),
                        ),
                        const SizedBox(width: 10),
                        const Text('Discovery Map', style: TextStyle(color: Color(0xFF3D405B), fontWeight: FontWeight.w900, fontSize: 20)),
                        const Spacer(),
                        Material(
                          color: Colors.white,
                          shape: const CircleBorder(),
                          elevation: 0,
                          child: IconButton(
                            icon: const Icon(Icons.zoom_out_map, color: Color(0xFF3D405B), size: 22),
                            onPressed: () {
                              final currentBounds = _getEventBounds();
                              setState(() => _selectedEvent = null);
                              
                              if (currentBounds != null) {
                                final target = CameraFit.bounds(
                                  bounds: currentBounds, 
                                  padding: _mapFitPadding,
                                  maxZoom: 10.0,
                                ).fit(_mapController.camera);
                                
                                _animatedMapMove(target.center, target.zoom);
                                
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Viewing all events 🗺️'), 
                                    duration: Duration(seconds: 1),
                                  ),
                                );
                              } else {
                                _animatedMapMove(_malaysiaCenter, _defaultZoom);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // 3. Right side zoom buttons (+ and -)
          Positioned(
            right: 16,
            top: MediaQuery.of(context).padding.top + 80,
            child: Column(
              children: [
                FloatingActionButton.small(
                  heroTag: 'zoomIn',
                  backgroundColor: Colors.white.withValues(alpha: 0.95),
                  foregroundColor: const Color(0xFF3D405B),
                  onPressed: _zoomIn,
                  child: const Icon(Icons.add, size: 20),
                ),
                const SizedBox(height: 8),
                FloatingActionButton.small(
                  heroTag: 'zoomOut',
                  backgroundColor: Colors.white.withValues(alpha: 0.95),
                  foregroundColor: const Color(0xFF3D405B),
                  onPressed: _zoomOut,
                  child: const Icon(Icons.remove, size: 20),
                ),
              ],
            ),
          ),

          // 4. Bottom pop-up event detail card
          Positioned(
            left: 20, right: 20, bottom: 120,
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              transitionBuilder: (child, animation) {
                return SlideTransition(
                  position: Tween<Offset>(begin: const Offset(0, 0.4), end: Offset.zero)
                      .animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic)),
                  child: FadeTransition(opacity: animation, child: child),
                );
              },
              child: _selectedEvent != null
                  ? GestureDetector(
                      key: ValueKey(_selectedEvent!.id), 
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => EventDetailScreen(event: _selectedEvent!))),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.95),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.15), blurRadius: 20, offset: const Offset(0, 10))],
                        ),
                        child: Row(
                          children: [
                            ClipRRect(
                              borderRadius: BorderRadius.circular(14),
                              child: Image.network(_selectedEvent!.imageUrl, width: 70, height: 70, fit: BoxFit.cover),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(_selectedEvent!.category, style: const TextStyle(color: Color(0xFFE07A5F), fontSize: 10, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 4),
                                  Text(_selectedEvent!.title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15, color: Color(0xFF3D405B))),
                                  const SizedBox(height: 4),
                                  Text(_selectedEvent!.address, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                                ],
                              ),
                            ),
                            const SizedBox(width: 10),
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: const BoxDecoration(color: Color(0xFF81B29A), shape: BoxShape.circle),
                              child: const Icon(Icons.arrow_forward_ios, size: 14, color: Colors.white),
                            ),
                          ],
                        ),
                      ),
                    )
                  : const SizedBox.shrink(),
            ),
          ),
        ],
      ),
    );
  }
}