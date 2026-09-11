class TourismEvent {
  final String id;
  final String title;
  final String description;
  final String category; // Culture, Food, Festival, Heritage, Nature
  final String location; 
  final String state;    
  final DateTime date;
  final String time;     // e.g. "10:00 AM", "3:30 PM"
  final double priceInMyr; 
  final String imageUrl;
  final String recommendationReason; 
  final double latitude;
  final double longitude;

  const TourismEvent({
    required this.id,
    required this.title,
    required this.description,
    required this.category,
    required this.location,
    required this.state,
    required this.date,
    required this.time,
    required this.priceInMyr,
    required this.imageUrl,
    required this.recommendationReason,
    required this.latitude,
    required this.longitude,
  });
}