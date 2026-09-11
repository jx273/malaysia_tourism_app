import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../models/tourism_event.dart';
import 'event_detail_screen.dart';

class AiRecommendScreen extends StatefulWidget {
  const AiRecommendScreen({super.key});

  @override
  State<AiRecommendScreen> createState() => _AiRecommendScreenState();
}

class _AiRecommendScreenState extends State<AiRecommendScreen> {
  final List<String> _interests = [
    'Cultural Heritage',
    'Traditional Crafts',
    'Rainforest Music',
    'Street Food Walks',
    'Indigenous Arts',
  ];

  final Set<String> _selectedInterests = {'Cultural Heritage', 'Traditional Crafts'};
  bool _isGenerating = false;
  List<TourismEvent> _recommendations = [];

  @override
  void initState() {
    super.initState();
    _generateMockAiPlan();
  }

  void _generateMockAiPlan() {
    setState(() {
      _isGenerating = true;
    });

    Future.delayed(const Duration(milliseconds: 400), () {
      if (mounted) {
        setState(() {
          _isGenerating = false;
          _recommendations = MockEventRepository.events.take(3).toList();
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.auto_awesome, color: Color(0xFF007A3D), size: 20),
            SizedBox(width: 8),
            Text(
              'AI Recommendations',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
          ],
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Your Travel Preferences',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF0F172A)),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Select what you want to experience. Our algorithm will match local events accordingly.',
                      style: TextStyle(fontSize: 12, color: Colors.grey.shade600, height: 1.4),
                    ),
                    const SizedBox(height: 12),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _interests.map((interest) {
                        final isSelected = _selectedInterests.contains(interest);
                        return FilterChip(
                          showCheckmark: false,
                          label: Text(interest),
                          selected: isSelected,
                          selectedColor: const Color(0xFF007A3D),
                          labelStyle: TextStyle(
                            color: isSelected ? Colors.white : const Color(0xFF475569),
                            fontSize: 11,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                          backgroundColor: const Color(0xFFF1F5F9),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          side: BorderSide(
                            color: isSelected ? Colors.transparent : Colors.grey.shade200,
                          ),
                          onSelected: (selected) {
                            setState(() {
                              if (selected) {
                                _selectedInterests.add(interest);
                              } else {
                                _selectedInterests.remove(interest);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 14),
                    SizedBox(
                      width: double.infinity,
                      height: 44,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF007A3D),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        icon: const Icon(Icons.refresh, size: 16),
                        label: const Text('Update Recommendations', style: TextStyle(fontWeight: FontWeight.bold)),
                        onPressed: _generateMockAiPlan,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              const Text(
                'Matched Experiences',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
              ),
              const SizedBox(height: 10),

              if (_isGenerating)
                const Padding(
                  padding: EdgeInsets.all(40),
                  child: Center(child: CircularProgressIndicator(color: Color(0xFF007A3D))),
                )
              else
                ..._recommendations.map((event) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEFF6FF),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Row(
                                children: [
                                  Icon(Icons.stars, color: Color(0xFF2563EB), size: 13),
                                  SizedBox(width: 4),
                                  Text(
                                    'High Match',
                                    style: TextStyle(color: Color(0xFF2563EB), fontSize: 11, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                            ),
                            const Spacer(),
                            Text(
                              event.priceInMyr == 0 ? 'Free' : 'RM ${event.priceInMyr.toStringAsFixed(0)}',
                              style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF007A3D)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          event.title,
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Why: ${event.recommendationReason}',
                          style: TextStyle(fontSize: 12, color: Colors.grey.shade700, fontStyle: FontStyle.italic),
                        ),
                        const SizedBox(height: 10),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(builder: (context) => EventDetailScreen(event: event)),
                              );
                            },
                            child: const Text('View Details →', style: TextStyle(color: Color(0xFF007A3D))),
                          ),
                        ),
                      ],
                    ),
                  );
                }),
            ],
          ),
        ),
      ),
    );
  }
}