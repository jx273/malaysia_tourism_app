import 'package:flutter/foundation.dart';
import '../models/tourism_event.dart';
import '../widgets/pixel_mascot.dart';

class MockEventRepository {
  static final List<TourismEvent> events = [
    TourismEvent(
      id: 'e1',
      title: 'George Town Heritage Trail & Craft Tour',
      description:
          'Stroll through UNESCO World Heritage shophouses, discover traditional joss stick making, and sample authentic street heritage food.',
      category: 'Heritage',
      location: 'George Town',
      state: 'Penang',
      date: DateTime(2026, 9, 20),
      time: '09:30 AM',
      priceInMyr: 0.0,
      imageUrl: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Highly rated walking route for authentic living heritage and artisan trades.',
      latitude: 5.4141,
      longitude: 100.3288,
    ),
    TourismEvent(
      id: 'e2',
      title: 'Sarawak Rainforest World Music Showcase',
      description:
          'Experience the rhythm of indigenous Borneo instruments, sape masterclasses, and vibrant cultural dance performances.',
      category: 'Festival',
      location: 'Sarawak Cultural Village',
      state: 'Sarawak',
      date: DateTime(2026, 9, 22),
      time: '04:00 PM',
      priceInMyr: 120.0,
      imageUrl: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Top global musical gathering spotlighting indigenous Bornean arts and nature.',
      latitude: 1.7503,
      longitude: 110.3175,
    ),
    TourismEvent(
      id: 'e3',
      title: 'Jonker Street Twilight Culture & Food Market',
      description:
          'Historic Melaka evening exploration with Peranakan delicacies, live street performances, and antique crafts.',
      category: 'Food',
      location: 'Banda Hilir',
      state: 'Melaka',
      date: DateTime(2026, 9, 25),
      time: '06:30 PM',
      priceInMyr: 0.0,
      imageUrl: 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Essential cultural night walk famous for Nyonya culinary heritage.',
      latitude: 2.1944,
      longitude: 102.2491,
    ),
    TourismEvent(
      id: 'e4',
      title: 'Sabah Cultural Harvest & Dance Gathering',
      description:
          'Immerse in the harvest celebrations of Kadazan-Dusun traditions with rhythmic bamboo dancing and local culinary arts.',
      category: 'Culture',
      location: 'Penampang Cultural Grounds',
      state: 'Sabah',
      date: DateTime(2026, 9, 28),
      time: '11:00 AM',
      priceInMyr: 20.0,
      imageUrl: 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Authentic celebration of local East Malaysian indigenous harvest rituals.',
      latitude: 5.9221,
      longitude: 116.0886,
    ),
    TourismEvent(
      id: 'e5',
      title: 'Johor Bahru Old Town Heritage & Coffee Trail',
      description:
          'Guided walk through ancient bakeries, century-old clan temples, and artisan coffee roasters in historic downtown JB.',
      category: 'Heritage',
      location: 'Jalan Tan Hiok Nee',
      state: 'Johor',
      date: DateTime(2026, 10, 2),
      time: '08:30 AM',
      priceInMyr: 15.0,
      imageUrl: 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=800&q=80',
      recommendationReason: 'Tranquil cultural morning trail discovering local Southern heritage flavors.',
      latitude: 1.4552,
      longitude: 103.7638,
    ),
  ];

  static List<String> get categories => [
        'All',
        'Culture',
        'Heritage',
        'Festival',
        'Food',
        'Nature',
      ];
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
      currentList.sort((a, b) => a.date.compareTo(b.date));
    }
    savedEvents.value = currentList;
  }
}

class MascotSettings {
  static final MascotSettings instance = MascotSettings._internal();
  MascotSettings._internal();

  final ValueNotifier<MascotType> currentMascot = ValueNotifier<MascotType>(MascotType.tapir);

  void toggleMascot() {
    if (currentMascot.value == MascotType.tapir) {
      currentMascot.value = MascotType.tiger;
    } else {
      currentMascot.value = MascotType.tapir;
    }
  }
}