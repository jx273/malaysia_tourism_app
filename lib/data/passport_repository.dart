import 'package:flutter/foundation.dart';
import '../models/tourism_event.dart';

class PostcardMemory {
  final String id;
  final TourismEvent event;
  final String note;
  final DateTime checkInTime;
  final String userPhotoUrl;

  PostcardMemory({
    required this.id,
    required this.event,
    required this.note,
    required this.checkInTime,
    required this.userPhotoUrl,
  });
}

class PassportRepository {
  static final PassportRepository instance = PassportRepository._internal();
  PassportRepository._internal();

  final ValueNotifier<List<PostcardMemory>> memories = ValueNotifier<List<PostcardMemory>>([
    PostcardMemory(
      id: 'mem_1',
      event: TourismEvent(
        id: 'evt002', // Updated to match the standardized event ID
        title: 'Pasar Karat JB',
        description: 'A popular night market offering clothes, antiques, and street food.',
        category: 'Market',
        address: 'Jalan Segget, 80000 Johor Bahru',
        state: 'Johor',
        startDate: null,
        openingTime: '20:00',
        priceInMyr: 0,
        imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSW5dwYpn5bsxJ82RsMApivcUMuCjj7b9oAajhJHOCWEF6UZKh42J-TlLfa&s=10',
        recommendationReason: 'A vibrant local experience.',
        latitude: 1.458,
        longitude: 103.764,
      ),
      note: 'Found super vintage souvenirs and delicious Otak-Otak!',
      checkInTime: DateTime(2026, 9, 15, 20, 30),
      userPhotoUrl: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80',
    ),
  ]);

  bool isCheckedIn(String eventId) {
    return memories.value.any((m) => m.event.id == eventId);
  }

  // New: Fetch an existing memory to support "Snap Again" / Editing
  PostcardMemory? getMemoryForEvent(String eventId) {
    try {
      return memories.value.firstWhere((m) => m.event.id == eventId);
    } catch (_) {
      return null;
    }
  }

  // Modified: Replace memory if one for this event already exists to prevent duplicates
  void addMemory(PostcardMemory memory) {
    final currentList = List<PostcardMemory>.from(memories.value);
    final existingIndex = currentList.indexWhere((m) => m.event.id == memory.event.id);
    
    if (existingIndex != -1) {
      currentList[existingIndex] = memory; // Update existing
    } else {
      currentList.insert(0, memory); // Add new
    }
    
    memories.value = currentList;
  }
}