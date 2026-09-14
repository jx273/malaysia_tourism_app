import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import '../widgets/pixel_mascot.dart';
import '../widgets/walking_mascot.dart';

class EventDetailScreen extends StatefulWidget {
  final TourismEvent event;

  const EventDetailScreen({super.key, required this.event});

  @override
  State<EventDetailScreen> createState() => _EventDetailScreenState();
}

class _EventDetailScreenState extends State<EventDetailScreen> {
  late bool _isInPlan;

  @override
  void initState() {
    super.initState();
    _isInPlan = PlanRepository.instance.isEventInPlan(widget.event.id);
  }

  void _openMascotChat(BuildContext context, TourismEvent event) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF0F172A),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return ValueListenableBuilder<MascotType>(
          valueListenable: UserSettings.instance.selectedMascot,
          builder: (context, currentMascot, _) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(context).viewInsets.bottom + 24,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      PixelMascot(
                        type: currentMascot,
                        action: MascotAction.happy,
                        size: 44,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              currentMascot == MascotType.tiger ? 'Tiger Cub Guide' : 'Ollie the Tapir',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 15,
                              ),
                            ),
                            Text(
                              'Ask me anything about ${event.title}!',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white54, size: 20),
                        onPressed: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ActionChip(
                        backgroundColor: const Color(0xFF1E293B),
                        label: const Text('Best time to visit?', style: TextStyle(color: Colors.white, fontSize: 11)),
                        side: const BorderSide(color: Color(0xFF334155)),
                        onPressed: () {},
                      ),
                      ActionChip(
                        backgroundColor: const Color(0xFF1E293B),
                        label: const Text('Is it crowded?', style: TextStyle(color: Colors.white, fontSize: 11)),
                        side: const BorderSide(color: Color(0xFF334155)),
                        onPressed: () {},
                      ),
                      ActionChip(
                        backgroundColor: const Color(0xFF1E293B),
                        label: const Text('Wheelchair accessible?', style: TextStyle(color: Colors.white, fontSize: 11)),
                        side: const BorderSide(color: Color(0xFF334155)),
                        onPressed: () {},
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  TextField(
                    style: const TextStyle(color: Colors.white, fontSize: 13),
                    decoration: InputDecoration(
                      hintText: 'Ask guide about this activity...',
                      hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
                      filled: true,
                      fillColor: const Color(0xFF1E293B),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      suffixIcon: const Icon(Icons.send, color: Color(0xFF007A3D), size: 18),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  void _handleTogglePlan() {
    PlanRepository.instance.togglePlan(widget.event);
    setState(() {
      _isInPlan = PlanRepository.instance.isEventInPlan(widget.event.id);
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          _isInPlan ? 'Added to your Personal Plan!' : 'Removed from your Plan',
        ),
        duration: const Duration(milliseconds: 1200),
        backgroundColor: const Color(0xFF0F172A),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final event = widget.event;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: Stack(
            children: [
              Column(
                children: [
                  Expanded(
                    child: CustomScrollView(
                      slivers: [
                        SliverAppBar(
                          expandedHeight: 250,
                          pinned: true,
                          leading: Padding(
                            padding: const EdgeInsets.all(8.0),
                            child: CircleAvatar(
                              backgroundColor: Colors.white.withOpacity(0.85),
                              child: IconButton(
                                icon: const Icon(Icons.arrow_back, color: Color(0xFF0F172A), size: 18),
                                onPressed: () => Navigator.pop(context),
                              ),
                            ),
                          ),
                          flexibleSpace: FlexibleSpaceBar(
                            background: Image.network(
                              event.imageUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) => Container(
                                color: Colors.grey.shade200,
                                child: const Icon(Icons.image_not_supported, color: Colors.grey),
                              ),
                            ),
                          ),
                        ),
                        SliverToBoxAdapter(
                          child: Padding(
                            padding: const EdgeInsets.all(20),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF007A3D).withOpacity(0.1),
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: Text(
                                        event.category,
                                        style: const TextStyle(
                                          color: Color(0xFF007A3D),
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ),
                                    Text(
                                      event.priceInMyr == 0 ? 'Free Entry' : 'RM ${event.priceInMyr.toStringAsFixed(0)}',
                                      style: const TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w900,
                                        color: Color(0xFF007A3D),
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  event.title,
                                  style: const TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                const SizedBox(height: 14),
                                Container(
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(14),
                                    border: Border.all(color: Colors.grey.shade200),
                                  ),
                                  child: Column(
                                    children: [
                                      Row(
                                        children: [
                                          const Icon(Icons.place_outlined, size: 16, color: Color(0xFF007A3D)),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(
                                              '${event.location}, ${event.state}',
                                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                                            ),
                                          ),
                                        ],
                                      ),
                                      Divider(height: 20, color: Colors.grey.shade100),
                                      Row(
                                        children: [
                                          const Icon(Icons.calendar_today_outlined, size: 15, color: Color(0xFF007A3D)),
                                          const SizedBox(width: 8),
                                          Text(
                                            '${event.date.day}/${event.date.month}/${event.date.year}  at  ${event.time}',
                                            style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 20),
                                const Text(
                                  'Why Recommended',
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFEFF6FF),
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: const Color(0xFFBFDBFE)),
                                  ),
                                  child: Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const Icon(Icons.auto_awesome, color: Color(0xFF2563EB), size: 16),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          event.recommendationReason,
                                          style: const TextStyle(
                                            color: Color(0xFF1E40AF),
                                            fontSize: 12,
                                            height: 1.4,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(height: 20),
                                const Text(
                                  'About This Experience',
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  event.description,
                                  style: TextStyle(
                                    color: Colors.grey.shade700,
                                    fontSize: 13,
                                    height: 1.6,
                                  ),
                                ),
                                const SizedBox(height: 80),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      border: Border(top: BorderSide(color: Colors.grey.shade200)),
                    ),
                    child: SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _isInPlan ? const Color(0xFF0F172A) : const Color(0xFF007A3D),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                        icon: Icon(_isInPlan ? Icons.check : Icons.add, size: 18),
                        label: Text(
                          _isInPlan ? 'Added to My Plan (Tap to Remove)' : 'Add to Personal Plan',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        onPressed: _handleTogglePlan,
                      ),
                    ),
                  ),
                ],
              ),
              Positioned(
                left: 0,
                right: 0,
                bottom: 80,
                child: SizedBox(
                  height: 100,
                  child: Stack(
                    clipBehavior: Clip.none,
                    children: [
                      WalkingMascot(
                        speechText: 'Ask about event',
                        onTap: () => _openMascotChat(context, event),
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
  }
}