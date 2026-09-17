class TourismEvent {
  final String id;
  final String title;
  final String description;
  final String category;
  final String address; // 完整地址
  final String state;   // 州属
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
    double parsedPrice = 0.0;
    if (json['price'] != null) {
      final priceStr = json['price'].toString().replaceAll('RM', '').trim();
      parsedPrice = double.tryParse(priceStr) ?? 0.0;
    }
    return TourismEvent(
      id: json['event_id'] ?? 'evt_${json['id'] ?? '0'}',
      title: json['name'] ?? 'Untitled Event',
      description: json['description'] ?? '',
      category: json['category'] ?? 'Heritage',
      address: json['address'] ?? '',
      state: _extractState(json['address'] ?? 'Johor'),
      startDate: json['start_date'] != null && json['start_date'].toString().isNotEmpty ? DateTime.tryParse(json['start_date']) : null,
      endDate: json['end_date'] != null && json['end_date'].toString().isNotEmpty ? DateTime.tryParse(json['end_date']) : null,
      openingTime: json['opening_time'],
      closingTime: json['closing_time'],
      priceInMyr: parsedPrice,
      imageUrl: (json['image_url'] != null && json['image_url'].toString().startsWith('http')) ? json['image_url'] : 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?auto=format&fit=crop&w=800&q=80',
      recommendationReason: json['recommendation_reason'] ?? '',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 1.458,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 103.764,
    );
  }

  static String _extractState(String address) {
    // 简单的从地址中提取州属，兼容后端的 address 字段
    if (address.toLowerCase().contains('penang') || address.toLowerCase().contains('pulau pinang')) return 'Pulau Pinang';
    if (address.toLowerCase().contains('kuala lumpur')) return 'W.P. Kuala Lumpur';
    return 'Johor';
  }
}