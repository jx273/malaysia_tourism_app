import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../data/passport_repository.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import '../widgets/mascot_chat_sheet.dart';
import '../widgets/pixel_mascot.dart';

class EventDetailScreen extends StatefulWidget {
  final TourismEvent event;
  const EventDetailScreen({super.key, required this.event});

  @override
  State<EventDetailScreen> createState() => _EventDetailScreenState();
}

class _EventDetailScreenState extends State<EventDetailScreen> {
  final PassportRepository _planRepo = PassportRepository.instance;
  final ImagePicker _picker = ImagePicker();
  bool _isInPlan = false;

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

  Future<void> _takePhotoAndCheckInSafe() async {
    String finalPhotoPath = widget.event.imageUrl; 
    try {
      if (Platform.isIOS || Platform.isAndroid) {
        final XFile? photo = await _picker.pickImage(source: ImageSource.camera);
        if (photo != null) {
          finalPhotoPath = photo.path;
        } else {
          return;
        }
      } else {
        await Future.delayed(const Duration(milliseconds: 300));
      }
    } catch (e) {
      debugPrint("Camera unavailable, using fallback.");
    }

    if (!mounted) return;

    // Check if memory already exists for this event
    final existingMem = PassportRepository.instance.getMemoryForEvent(widget.event.id);
    String initialNote = "";
    if (existingMem != null && existingMem.note != "Had a great time here!") {
      initialNote = existingMem.note;
    }

    final noteController = TextEditingController(text: initialNote);
    final GlobalKey boundaryKey = GlobalKey(); // Kept for layout boundary structure
    final now = DateTime.now();
    final timeString = TimeOfDay.fromDateTime(now).format(context);
    final dateString = '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFFF4F1DE),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        contentPadding: const EdgeInsets.all(16),
        content: SingleChildScrollView(
          child: Column(
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
                              child: finalPhotoPath.startsWith('http') 
                                  ? Image.network(finalPhotoPath, fit: BoxFit.cover)
                                  : Image.file(File(finalPhotoPath), fit: BoxFit.cover),
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
                        widget.event.title, 
                        textAlign: TextAlign.center, 
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 12, color: Color(0xFF3D405B))
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: noteController,
                        maxLines: 3,
                        maxLength: 80, 
                        textAlign: TextAlign.center, 
                        style: const TextStyle(fontSize: 10, fontStyle: FontStyle.italic, color: Color(0xFFE07A5F), fontWeight: FontWeight.bold),
                        decoration: InputDecoration(
                          hintText: 'Tap to write a note about this memory',
                          hintStyle: TextStyle(color: const Color(0xFFE07A5F).withValues(alpha: 0.5)),
                          filled: true,
                          fillColor: const Color(0xFFF4F1DE).withValues(alpha: 0.5),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                          counterText: '', 
                        ),
                      ),
                      const SizedBox(height: 4),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        actionsAlignment: MainAxisAlignment.spaceBetween,
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel', style: TextStyle(color: Colors.grey))),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF81B29A),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () {
              final finalNote = noteController.text.trim().isEmpty ? "Had a great time here!" : noteController.text.trim();
              PassportRepository.instance.addMemory(
                PostcardMemory(
                  id: existingMem?.id ?? 'mem_${DateTime.now().millisecondsSinceEpoch}',
                  event: widget.event,
                  note: finalNote,
                  checkInTime: now,
                  userPhotoUrl: finalPhotoPath,
                ),
              );
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('🎉 Saved to Passport!')));
              setState(() {}); 
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isCheckedIn = PassportRepository.instance.isCheckedIn(widget.event.id);
    
    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      body: Stack(
        children: [
          CustomScrollView(
            slivers: [
              SliverAppBar(
                expandedHeight: 280,
                pinned: true,
                backgroundColor: const Color(0xFFF4F1DE),
                leading: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: CircleAvatar(
                    backgroundColor: Colors.white.withValues(alpha: 0.8),
                    child: IconButton(icon: const Icon(Icons.arrow_back, color: Color(0xFF3D405B)), onPressed: () => Navigator.pop(context)),
                  ),
                ),
                flexibleSpace: FlexibleSpaceBar(
                  background: Image.network(widget.event.imageUrl, fit: BoxFit.cover),
                ),
              ),
              
              SliverToBoxAdapter(
                child: Transform.translate(
                  offset: const Offset(0, -24), 
                  child: Container(
                    padding: const EdgeInsets.fromLTRB(20, 36, 20, 100),
                    decoration: const BoxDecoration(
                      color: Color(0xFFF4F1DE), 
                      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: const Color(0xFF3D405B), borderRadius: BorderRadius.circular(6)),
                              child: Text(widget.event.category, style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                            ),
                            Text(widget.event.priceInMyr == 0 ? 'Free Entry' : 'RM ${widget.event.priceInMyr.toInt()}', style: const TextStyle(color: Color(0xFF81B29A), fontWeight: FontWeight.w900, fontSize: 14)),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(widget.event.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF3D405B), height: 1.2)),
                        const SizedBox(height: 24),

                        _infoRow(Icons.place, 'Address', widget.event.address),
                        const SizedBox(height: 12),
                        _infoRow(Icons.calendar_today, 'Dates', (widget.event.startDate != null && widget.event.endDate != null) 
    ? '${widget.event.startDate!.toString().split(' ')[0]} to ${widget.event.endDate!.toString().split(' ')[0]}'
    : 'Open all year round'),
                        const SizedBox(height: 12),
                        _infoRow(Icons.access_time, 'Operating Hours', '${widget.event.openingTime ?? "09:00"} - ${widget.event.closingTime ?? "18:00"}'),
                        const SizedBox(height: 24),

                        Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(color: const Color(0xFFF2CC8F).withValues(alpha: 0.4), borderRadius: BorderRadius.circular(12)),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(Icons.format_quote, color: Color(0xFFE07A5F), size: 20),
                              const SizedBox(width: 10),
                              Expanded(child: Text(widget.event.recommendationReason, style: const TextStyle(color: Color(0xFFE07A5F), fontSize: 13, fontStyle: FontStyle.italic, fontWeight: FontWeight.bold))),
                            ],
                          ),
                        ),
                        const SizedBox(height: 24),
                        const Text('About this experience', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: Color(0xFF3D405B))),
                        const SizedBox(height: 12),
                        Text(widget.event.description, style: const TextStyle(color: Colors.black87, height: 1.6, fontSize: 13)),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          Positioned(
            right: 16,
            bottom: 100, 
            child: GestureDetector(
              onTap: () {
                showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  backgroundColor: Colors.transparent,
                  barrierColor: Colors.black.withValues(alpha: 0.3),
                  builder: (_) => MascotChatSheet(currentEvent: widget.event),
                );
              },
              child: ValueListenableBuilder<MascotType>(
                valueListenable: UserSettings.instance.selectedMascot,
                builder: (_, mascot, _) => Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle, border: Border.all(color: const Color(0xFFE07A5F), width: 1.5), boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 8)]),
                  child: PixelMascot(type: mascot, action: MascotAction.idleFront, size: 40),
                ),
              ),
            ),
          ),

          Positioned(
            left: 0, right: 0, bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 30),
              decoration: BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.05), blurRadius: 15, offset: const Offset(0, -5))]),
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isCheckedIn ? const Color(0xFFF2CC8F) : const Color(0xFF81B29A),
                        foregroundColor: isCheckedIn ? const Color(0xFF3D405B) : Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        elevation: 0,
                      ),
                      icon: Icon(isCheckedIn ? Icons.camera_alt : Icons.camera_alt_outlined, size: 20),
                      label: Text(isCheckedIn ? 'Snap Again' : 'Check-in', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
                      onPressed: _takePhotoAndCheckInSafe, 
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFE07A5F),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        elevation: 0,
                      ),
                      icon: Icon(_isInPlan ? Icons.bookmark : Icons.bookmark_border, size: 20),
                      label: Text(_isInPlan ? 'Saved' : 'Add to Plan', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
                      onPressed: () => setState(() => _isInPlan = !_isInPlan),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(IconData icon, String title, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 16, color: Colors.grey.shade400),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: TextStyle(fontSize: 11, color: Colors.grey.shade500)),
              const SizedBox(height: 2),
              Text(value, style: const TextStyle(fontSize: 13, color: Color(0xFF3D405B), fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ],
    );
  }
}