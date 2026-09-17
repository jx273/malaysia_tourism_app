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
    // 默认提供一张已打卡回忆，方便评委直接看到照片墙效果
    PostcardMemory(
      id: 'mem_1',
      event: TourismEvent(
        id: 'evt101',
        title: 'Pasar Karat JB Night Heritage',
        description: 'A vibrant popular night market in Johor Bahru.',
        category: 'Market',
        address: 'Jalan Segget',
        state: 'Johor',
        startDate: DateTime(2026, 9, 20),
        openingTime: '08:00 PM',
        priceInMyr: 0,
        imageUrl: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
        recommendationReason: 'A vibrant local street trading experience.',
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

  void addMemory(PostcardMemory memory) {
    memories.value = [memory, ...memories.value];
  }
}