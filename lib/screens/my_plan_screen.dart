import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../data/passport_repository.dart';
import '../models/tourism_event.dart';
import 'event_detail_screen.dart';

class MyPlanScreen extends StatelessWidget {
  const MyPlanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final planRepo = PlanRepository.instance;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text('My Travel Plan', style: TextStyle(color: Color(0xFF3D405B), fontWeight: FontWeight.w900, fontSize: 20)),
      ),
      body: Stack(
        children: [
          // 确保全局印花置于最底层
          Positioned.fill(child: CustomPaint(painter: _PatternPainter())),
          
          ValueListenableBuilder<List<TourismEvent>>(
            valueListenable: planRepo.savedEvents,
            builder: (context, saved, _) {
              if (saved.isEmpty) {
                return const Center(child: Text('No plans yet. Bookmark events to start!', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.w600)));
              }

              final totalCost = saved.fold(0.0, (sum, ev) => sum + ev.priceInMyr);

              return ListView(
                padding: const EdgeInsets.fromLTRB(20, 10, 20, 120),
                physics: const BouncingScrollPhysics(),
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                    decoration: BoxDecoration(color: const Color(0xFFE07A5F), borderRadius: BorderRadius.circular(20)),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Planned Events', style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 12, fontWeight: FontWeight.w600)),
                            const SizedBox(height: 4),
                            Text('${saved.length} Experiences Saved', style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(color: Colors.white.withOpacity(0.2), borderRadius: BorderRadius.circular(12)),
                          child: Text('Est. RM ${totalCost.toInt()}', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: saved.length,
                    itemBuilder: (context, idx) {
                      final ev = saved[idx];
                      final isCheckedIn = PassportRepository.instance.isCheckedIn(ev.id);
                      final isLast = idx == saved.length - 1;
                      
                      // 时间轴圆点颜色严格跟随状态 (已打卡=黄色，未打卡=绿色)
                      final dotColor = isCheckedIn ? const Color(0xFFF2CC8F) : const Color(0xFF81B29A);

                      return IntrinsicHeight(
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            SizedBox(
                              width: 24,
                              child: Column(
                                children: [
                                  Container(width: 12, height: 12, decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle)),
                                  if (!isLast) Expanded(child: Container(width: 2, color: Colors.grey.shade300)),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: GestureDetector(
                                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => EventDetailScreen(event: ev))),
                                child: Container(
                                  margin: const EdgeInsets.only(bottom: 20),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.85),
                                    borderRadius: BorderRadius.circular(16),
                                    border: Border.all(color: Colors.grey.shade200, width: 1.5),
                                    boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))],
                                  ),
                                  child: Row(
                                    children: [
                                      ClipRRect(
                                        borderRadius: const BorderRadius.horizontal(left: Radius.circular(14)),
                                        child: Image.network(ev.imageUrl, width: 90, height: 90, fit: BoxFit.cover),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Padding(
                                          padding: const EdgeInsets.symmetric(vertical: 12),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            mainAxisAlignment: MainAxisAlignment.center,
                                            children: [
                                              Text(
                                                '${ev.startDate?.day ?? 20}/${ev.startDate?.month ?? 9}/2026 • ${ev.openingTime ?? "09:30 AM"}',
                                                style: const TextStyle(fontSize: 10, color: Color(0xFFE07A5F), fontWeight: FontWeight.w900),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(ev.title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF3D405B))),
                                              const SizedBox(height: 4),
                                              Text('${ev.address}, ${ev.state}', maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
                                              const SizedBox(height: 6),
                                              Row(
                                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                                children: [
                                                  Row(
                                                    children: [
                                                      Icon(isCheckedIn ? Icons.check_circle : Icons.camera_alt, size: 14, color: isCheckedIn ? const Color(0xFFD4AC0D) : const Color(0xFF81B29A)),
                                                      const SizedBox(width: 4),
                                                      Text(isCheckedIn ? 'Visited' : 'Check-in', style: TextStyle(color: isCheckedIn ? const Color(0xFFD4AC0D) : const Color(0xFF81B29A), fontSize: 11, fontWeight: FontWeight.bold)),
                                                    ],
                                                  ),
                                                  GestureDetector(
                                                    onTap: () => planRepo.togglePlan(ev),
                                                    child: Container(
                                                      padding: const EdgeInsets.all(4),
                                                      decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: Colors.red.shade200)),
                                                      child: const Icon(Icons.remove, size: 12, color: Colors.red),
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                    ],
                                  ),
                                ),
                              ),
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
        ],
      ),
    );
  }
}

class _PatternPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0xFF3D405B).withOpacity(0.07);
    const spacing = 30.0;
    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        final offsetX = (y / spacing) % 2 == 0 ? x : x + spacing / 2;
        canvas.drawCircle(Offset(offsetX, y), 2.5, paint);
      }
    }
  }
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}