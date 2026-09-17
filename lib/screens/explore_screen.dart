import 'package:flutter/material.dart';
import '../data/mock_events.dart';
import '../models/tourism_event.dart';
import 'event_detail_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  String _selectedCategory = 'All';
  String _searchQuery = '';
  final Set<String> _selectedAiPreferences = {'Cultural Heritage'};

  final List<String> _aiPreferences = [
    'Cultural Heritage',
    'Traditional Crafts',
    'Street Food Walks',
    'Indigenous Arts',
    'Nature & Eco',
  ];

  @override
  Widget build(BuildContext context) {
    final filteredEvents = MockEventRepository.events.where((e) {
      final matchCat = _selectedCategory == 'All' || e.category == _selectedCategory;
      final matchSearch = e.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          e.location.toLowerCase().contains(_searchQuery.toLowerCase()) ||
          e.state.toLowerCase().contains(_searchQuery.toLowerCase());
      return matchCat && matchSearch;
    }).toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          'Explore Events',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 1. 搜索框
              TextField(
                onChanged: (val) => setState(() => _searchQuery = val),
                decoration: InputDecoration(
                  hintText: 'Search by event or state...',
                  prefixIcon: const Icon(Icons.search, color: Color(0xFF007A3D)),
                  filled: true,
                  fillColor: Colors.white,
                  contentPadding: const EdgeInsets.symmetric(vertical: 12),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(color: Colors.grey.shade200),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(14),
                    borderSide: BorderSide(color: Colors.grey.shade200),
                  ),
                ),
              ),
              const SizedBox(height: 14),

              // 2. 搬迁整合进来的 AI 智能偏好过滤栏
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome, color: Color(0xFF2563EB), size: 16),
                        SizedBox(width: 6),
                        Text(
                          'AI Recommendation Filters',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1E40AF),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: _aiPreferences.map((pref) {
                        final isSel = _selectedAiPreferences.contains(pref);
                        return FilterChip(
                          showCheckmark: false,
                          label: Text(pref),
                          selected: isSel,
                          selectedColor: const Color(0xFF2563EB),
                          labelStyle: TextStyle(
                            color: isSel ? Colors.white : const Color(0xFF1E40AF),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                          backgroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          side: BorderSide(color: isSel ? Colors.transparent : const Color(0xFFBFDBFE)),
                          onSelected: (selected) {
                            setState(() {
                              if (selected) {
                                _selectedAiPreferences.add(pref);
                              } else {
                                _selectedAiPreferences.remove(pref);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // 3. 常规分类 Pills
              SizedBox(
                height: 36,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: MockEventRepository.categories.length,
                  itemBuilder: (context, index) {
                    final cat = MockEventRepository.categories[index];
                    final isSel = cat == _selectedCategory;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        showCheckmark: false,
                        label: Text(cat),
                        selected: isSel,
                        selectedColor: const Color(0xFF007A3D),
                        backgroundColor: Colors.white,
                        labelStyle: TextStyle(
                          color: isSel ? Colors.white : Colors.grey.shade700,
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                        ),
                        side: BorderSide(color: isSel ? Colors.transparent : Colors.grey.shade200),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        onSelected: (_) => setState(() => _selectedCategory = cat),
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 16),

              // 4. 活动卡片列表
              ...filteredEvents.map((event) {
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: Colors.grey.shade200),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(12),
                    leading: ClipRRect(
                      borderRadius: BorderRadius.circular(10),
                      child: Image.network(
                        event.imageUrl,
                        width: 65,
                        height: 65,
                        fit: BoxFit.cover,
                      ),
                    ),
                    title: Text(
                      event.title,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Text('${event.location}, ${event.state}', style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
                        const SizedBox(height: 2),
                        Text('${event.date.day}/${event.date.month} • ${event.time}',
                            style: const TextStyle(fontSize: 11, color: Color(0xFF007A3D), fontWeight: FontWeight.bold)),
                      ],
                    ),
                    trailing: Text(
                      event.priceInMyr == 0 ? 'Free' : 'RM ${event.priceInMyr.toStringAsFixed(0)}',
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF007A3D)),
                    ),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => EventDetailScreen(event: event)),
                      );
                    },
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