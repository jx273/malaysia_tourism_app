import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/tourism_event.dart';

class MockEventRepository {
  static List<TourismEvent> events = [
    TourismEvent(
      id: 'evt101',
      title: 'Pasar Karat JB Night Heritage',
      description: 'A vibrant popular night market in historic Johor Bahru.',
      category: 'Market',
      address: 'Jalan Segget',
      state: 'Johor',
      startDate: DateTime(2026, 9, 20),
      openingTime: '08:00 PM',
      priceInMyr: 0.0,
      imageUrl: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'A vibrant local street trading experience.',
      latitude: 1.458,
      longitude: 103.764,
    ),
    TourismEvent(
      id: 'evt102',
      title: 'Desaru Agro Heritage Tour',
      description: 'Award-winning agro-tourism site exploring tropical biodiversity.',
      category: 'Nature',
      address: 'Desaru Coast',
      state: 'Johor',
      startDate: DateTime(2026, 9, 22),
      openingTime: '09:00 AM',
      priceInMyr: 30.0,
      imageUrl: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Great eco-learning trail for families.',
      latitude: 1.594,
      longitude: 104.225,
    ),
    TourismEvent(
      id: 'evt103',
      title: 'Kota Tinggi Riverine Exploration',
      description: 'Watch thousands of synchronised fireflies illuminate the riverbank.',
      category: 'Nature',
      address: 'Kota Tinggi',
      state: 'Johor',
      startDate: DateTime(2026, 9, 25),
      openingTime: '07:30 PM',
      priceInMyr: 20.0,
      imageUrl: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'A magical evening sustainable eco-experience.',
      latitude: 1.73,
      longitude: 103.89,
    ),
  ];

  static Future<void> fetchEventsFromBackend() async {
    const apiUrl = 'http://127.0.0.1:8000/app/events';
    try {
      final response = await http.get(Uri.parse(apiUrl)).timeout(const Duration(seconds: 3));
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        if (data.isNotEmpty) {
          events = data.map((json) => TourismEvent.fromJson(json)).toList();
        }
      }
    } catch (e) {
      debugPrint('Backend unreachable, using local fallback.');
    }
  }
}

class PlanRepository {
  static final PlanRepository instance = PlanRepository._internal();
  PlanRepository._internal();

  final ValueNotifier<List<TourismEvent>> savedEvents = ValueNotifier<List<TourismEvent>>([]);

  bool isEventInPlan(String eventId) {
    return savedEvents.value.any((e) => e.id == eventId);
  }

  void togglePlan(TourismEvent event) {
    final currentList = List<TourismEvent>.from(savedEvents.value);
    if (isEventInPlan(event.id)) {
      currentList.removeWhere((e) => e.id == event.id);
    } else {
      currentList.add(event);
      currentList.sort((a, b) {
        final aDate = a.startDate ?? DateTime.now();
        final bDate = b.startDate ?? DateTime.now();
        return aDate.compareTo(bDate);
      });
    }
    savedEvents.value = currentList;
  }
}