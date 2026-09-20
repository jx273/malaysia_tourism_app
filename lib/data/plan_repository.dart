import 'package:flutter/foundation.dart';
import '../models/tourism_event.dart';

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