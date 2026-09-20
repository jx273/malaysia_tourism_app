import 'package:flutter/foundation.dart';
import '../models/tourism_event.dart';
import '../services/api_service.dart';

class MockEventRepository {
  static List<TourismEvent> events = [
    // Default fallback events in case the backend is completely unreachable
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
    try {
      // Use the unified ApiService to ensure we respect the cross-platform IP rules
      final fetchedEvents = await ApiService.fetchEvents();
      if (fetchedEvents.isNotEmpty) {
        events = fetchedEvents;
      }
    } catch (e) {
      debugPrint('Backend unreachable, using local fallback events: $e');
    }
  }
}