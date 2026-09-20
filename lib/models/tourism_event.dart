class TourismEvent {
  final String id;
  final String title;
  final String description;
  final String category;
  final String address; 
  final String state;   
  final DateTime? startDate;
  final DateTime? endDate;
  final String? openingTime;
  final String? closingTime;
  final double priceInMyr;
  final String imageUrl;
  final String recommendationReason;
  final double latitude;
  final double longitude;

  const TourismEvent({
    required this.id, required this.title, required this.description,
    required this.category, required this.address, required this.state,
    this.startDate, this.endDate, this.openingTime, this.closingTime,
    required this.priceInMyr, required this.imageUrl,
    required this.recommendationReason, required this.latitude, required this.longitude,
  });

  factory TourismEvent.fromJson(Map<String, dynamic> json) {
    String rawImageUrl = json['image_url'] ?? '';

    String fallbackUrl = 'https://cdn.getyourguide.com/img/tour/1632e137c983caf9b17097bcaf70e24959f91f385acf4c836dab30c57997e2ad.png/68.jpg';

    String safeImageUrl = rawImageUrl;
    if (rawImageUrl.isNotEmpty && rawImageUrl.startsWith('http')) {
      if (!rawImageUrl.contains('unsplash.com') && !rawImageUrl.contains('gstatic.com')) {
        safeImageUrl = 'https://wsrv.nl/?url=${Uri.encodeComponent(rawImageUrl)}&default=${Uri.encodeComponent(fallbackUrl)}&output=jpg';
      }
    } else if (rawImageUrl.isEmpty) {
      safeImageUrl = 'https://wsrv.nl/?url=${Uri.encodeComponent(fallbackUrl)}&output=jpg';
    }

    DateTime? parseDate(dynamic val) {
      if (val == null) return null;
      if (val is DateTime) return val;
      if (val is String && val.trim().isNotEmpty) {
        return DateTime.tryParse(val.trim());
      }
      return null;
    }

    return TourismEvent(
      id: json['event_id'] ?? json['id'] ?? '',
      title: json['name'] ?? json['title'] ?? '',
      description: json['description'] ?? '',
      category: json['category'] ?? '',
      state: json['state'] ?? 'Johor',
      address: json['address'] ?? '',
      latitude: (json['latitude'] is num)
          ? (json['latitude'] as num).toDouble()
          : double.tryParse(json['latitude']?.toString() ?? '0') ?? 0.0,
      longitude: (json['longitude'] is num)
          ? (json['longitude'] as num).toDouble()
          : double.tryParse(json['longitude']?.toString() ?? '0') ?? 0.0,
      startDate: parseDate(json['start_date']),
      endDate: parseDate(json['end_date']),
      openingTime: json['opening_time'] ?? '',
      closingTime: json['closing_time'] ?? '',
      priceInMyr: (json['price'] is num)
          ? (json['price'] as num).toDouble()
          : double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      imageUrl: safeImageUrl,
      recommendationReason: json['recommendation_reason'] ?? '',
    );
  }
}