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

class _MapScreenState extends State<MapScreen> {
  final MapController _mapController = MapController();
  TourismEvent? _selectedEvent;
  
  final LatLng _malaysiaCenter = const LatLng(4.0, 109.0);
  final double _defaultZoom = 5.0;

  // 复古奶油地图滤镜
  final ColorFilter _mapThemeFilter = const ColorFilter.matrix([
    0.85, 0.1,  0.0,  0, 25, 
    0.1,  0.85, 0.1,  0, 30, 
    0.1,  0.1,  0.75, 0, 15, 
    0,    0,    0,    1, 0,  
  ]);

  void _zoomIn() {
    _mapController.move(_mapController.camera.center, _mapController.camera.zoom + 1.2);
  }

  void _zoomOut() {
    _mapController.move(_mapController.camera.center, _mapController.camera.zoom - 1.2);
  }

  @override
  Widget build(BuildContext context) {
    final events = MockEventRepository.events;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      body: Stack(
        children: [
          // 1. 底层地图
          ColorFiltered(
            colorFilter: _mapThemeFilter,
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: _malaysiaCenter,
                initialZoom: _defaultZoom,
                minZoom: 4.5,
                maxZoom: 18,
                cameraConstraint: CameraConstraint.contain(
                  bounds: LatLngBounds(const LatLng(-1.0, 97.0), const LatLng(9.0, 121.0)),
                ),
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
                      width: 120, 
                      height: 120,
                      child: Center(
                        child: GestureDetector(
                          behavior: HitTestBehavior.deferToChild,
                          onTap: () {
                            setState(() => _selectedEvent = ev);
                            _mapController.move(eventLocation, 13.0);
                          },
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              AnimatedScale(
                                scale: isSel ? 1.35 : 1.0,
                                duration: const Duration(milliseconds: 400),
                                curve: Curves.elasticOut,
                                child: Container(
                                  padding: const EdgeInsets.all(5),
                                  decoration: BoxDecoration(
                                    color: isSel ? const Color(0xFFE07A5F) : Colors.white,
                                    shape: BoxShape.circle,
                                    border: Border.all(color: isSel ? Colors.white : const Color(0xFF81B29A), width: 2.5),
                                    boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.25), blurRadius: 8, offset: const Offset(0, 3))],
                                  ),
                                  child: ValueListenableBuilder<MascotType>(
                                    valueListenable: UserSettings.instance.selectedMascot,
                                    builder: (_, mascotType, _) => PixelMascot(
                                      type: mascotType,
                                      action: isSel ? MascotAction.happy : MascotAction.idleFront,
                                      size: 38, 
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 4),
                              if (isSel)
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF3D405B), 
                                    borderRadius: BorderRadius.circular(8),
                                    boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.2), blurRadius: 4)],
                                  ),
                                  child: Text(ev.title.split(' ').first, style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                                )
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),

          // 2. 顶部标题栏 (去掉了阻挡点击的渐变色，保证右上角绝对能按到)
          Positioned(
            top: 0, left: 0, right: 0,
            child: SafeArea(
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
                    // 右上角返回默认中心按钮
                    Material(
                      color: Colors.white.withValues(alpha: 0.9),
                      shape: const CircleBorder(),
                      elevation: 4,
                      child: IconButton(
                        icon: const Icon(Icons.my_location, color: Color(0xFF3D405B), size: 22),
                        onPressed: () {
                          setState(() => _selectedEvent = null);
                          _mapController.move(_malaysiaCenter, _defaultZoom);
                        },
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // 3. 右侧缩放按钮 (+ 和 -)
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

          // 4. 底部弹出的活动详情卡片
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