import 'dart:ui';
import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import '../widgets/mascot_chat_sheet.dart';
import '../widgets/walking_mascot.dart';
import 'event_detail_screen.dart';
import '../services/api_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _searchController = TextEditingController();
  final List<String> _categories = [
    'All',
    'Culture',
    'Heritage',
    'Festival',
    'Food',
    'Nature',
    'Market'
  ];

  String _selectedCat = 'All';
  String _searchQuery = '';

  final List<Color> _cardColors = const [
    Color(0xFF81B29A), // 复古薄荷绿
    Color(0xFFF2CC8F), // 奶茶焦糖黄
    Color(0xFFE07A5F), // 潮流珊瑚红
    Color(0xFF3D405B), // 经典深靛蓝
  ];

  List<TourismEvent> _allEvents = []; 
  bool _isLoading = true;             
  String _errorMessage = '';          

  @override
  void initState() {
    super.initState();
    _fetchDataFromBackend(); 
  }

  Future<void> _fetchDataFromBackend() async {
    try {
      final events = await ApiService.fetchEvents();
      if (mounted) {
        setState(() {
          _allEvents = events;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  String _greeting(String userName) {
    final hour = DateTime.now().hour;
    final name = userName.trim().isNotEmpty ? userName : 'Explorer';
    
    if (hour < 12) return 'Good Morning, $name ☀️';
    if (hour < 18) return 'Good Afternoon, $name 🌿';
    return 'Good Evening, $name 🌙';
  }

  void _openEventDetail(TourismEvent event) {
    Navigator.push(
      context,
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 550),
        reverseTransitionDuration: const Duration(milliseconds: 400),
        pageBuilder: (_, _, _) => EventDetailScreen(event: event),
        transitionsBuilder: (_, animation, _, child) {
          final curve = CurvedAnimation(parent: animation, curve: Curves.easeOutCubic);
          return SlideTransition(
            position: Tween<Offset>(begin: const Offset(0, 1), end: Offset.zero).animate(curve),
            child: child,
          );
        },
      ),
    );
  }

  void _openMascotChat() async {
    print('正在向后端发送 AI 推荐请求...');
    
    final results = await ApiService.getAiRecommendations(
      lat: 1.45, 
      lng: 103.76, 
      interests: ['Culture', 'Nature']
    );
    
    print('拿到的 AI 推荐结果是: $results');

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      barrierColor: Colors.black.withValues(alpha: 0.3), 
      builder: (_) => const MascotChatSheet(),
    );
  }


  @override
  Widget build(BuildContext context) {
    // 如果正在加载，显示一个加载圈圈，防止白屏报错
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFFF4F1DE),
        body: Center(child: CircularProgressIndicator(color: Color(0xFFE07A5F))),
      );
    }

    // 如果报错了，显示错误信息
    if (_errorMessage.isNotEmpty) {
      return Scaffold(
        backgroundColor: const Color(0xFFF4F1DE),
        body: Center(child: Text('Oops! $_errorMessage', style: const TextStyle(color: Colors.red))),
      );
    }

    final filteredAllEvents = _allEvents.where((e) {
      final matchesCat = _selectedCat == 'All' || e.category.toLowerCase() == _selectedCat.toLowerCase();
      final q = _searchQuery.trim().toLowerCase();
      final matchesSearch = q.isEmpty ||
          e.title.toLowerCase().contains(q) ||
          e.address.toLowerCase().contains(q) ||
          e.state.toLowerCase().contains(q) ||
          e.category.toLowerCase().contains(q);
      return matchesCat && matchesSearch;
    }).toList();

    return Scaffold(
      backgroundColor: Colors.transparent,
      body: CustomPaint(
        painter: _PatternPainter(), 
        child: Stack(
        children: [
          SafeArea(
            bottom: false,
            child: ListView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.only(bottom: 140),
              children: [
                // 1. 顶部元气问候
                Padding(
                  padding: const EdgeInsets.fromLTRB(20, 16, 20, 14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ValueListenableBuilder<String>(
                        valueListenable: UserSettings.instance.userName,
                        builder: (context, userName, _) {
                          return Text(
                            _greeting(userName),
                            style: const TextStyle(
                              fontSize: 14,
                              color: Color(0xFFE07A5F),
                              fontWeight: FontWeight.w800,
                              letterSpacing: 0.5,
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Discover Malaysia',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF3D405B),
                          letterSpacing: -0.5,
                        ),
                      ),
                    ],
                  ),
                ),

                // 2. 真实生效的毛玻璃搜索栏
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(20),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 8, sigmaY: 8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.7),
                          borderRadius: BorderRadius.circular(20),
                          border: Border.all(color: Colors.white.withValues(alpha: 0.8), width: 1.5),
                        ),
                        child: TextField(
                          controller: _searchController,
                          onChanged: (val) => setState(() => _searchQuery = val),
                          style: const TextStyle(color: Color(0xFF3D405B), fontWeight: FontWeight.w600, fontSize: 14),
                          decoration: InputDecoration(
                            border: InputBorder.none,
                            hintText: 'Search heritage, night market, states...',
                            hintStyle: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.4), fontSize: 13),
                            icon: const Icon(Icons.search, color: Color(0xFF3D405B)),
                            suffixIcon: _searchQuery.isNotEmpty
                                ? IconButton(
                                    icon: const Icon(Icons.clear, size: 18, color: Colors.grey),
                                    onPressed: () {
                                      _searchController.clear();
                                      setState(() => _searchQuery = '');
                                    },
                                  )
                                : null,
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),

                // 3. 分类胶囊选择栏 (Category Pills)
                SizedBox(
                  height: 38,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    physics: const BouncingScrollPhysics(),
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: _categories.length,
                    itemBuilder: (context, index) {
                      final cat = _categories[index];
                      final isSel = _selectedCat == cat;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ActionChip(
                          elevation: isSel ? 3 : 0,
                          pressElevation: 1,
                          label: Text(
                            cat,
                            style: TextStyle(
                              // 被选中是白字，未选中是橙色字
                              color: isSel ? Colors.white : const Color(0xFFE07A5F),
                              fontWeight: FontWeight.w800,
                              fontSize: 12,
                            ),
                          ),
                          // 被选中是橙色背景，未选中是带透明的白底
                          backgroundColor: isSel ? const Color(0xFFE07A5F) : Colors.white.withValues(alpha: 0.65),
                          side: BorderSide.none,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                          onPressed: () => setState(() => _selectedCat = cat),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 24),

                // 4. Section 1：横向滑动的“所在州属特色卡片”
                ValueListenableBuilder<String>(
                  valueListenable: UserSettings.instance.selectedState,
                  builder: (context, state, _) {
                    final stateEvents = filteredAllEvents.where((e) => e.state.toLowerCase() == state.toLowerCase()).toList();

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 20),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'HAPPENING IN ${state.toUpperCase()} 📍',
                                style: const TextStyle(
                                  fontWeight: FontWeight.w900,
                                  fontSize: 13,
                                  color: Color(0xFF3D405B),
                                  letterSpacing: 1.2,
                                ),
                              ),
                              Text(
                                '${stateEvents.length} events',
                                style: const TextStyle(fontSize: 11, color: Color(0xFFE07A5F), fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 12),

                        if (stateEvents.isEmpty)
                          _emptyStateCard(state)
                        else
                          SizedBox(
                            height: 285,
                            child: ListView.builder(
                              scrollDirection: Axis.horizontal,
                              physics: const BouncingScrollPhysics(),
                              padding: const EdgeInsets.symmetric(horizontal: 20),
                              itemCount: stateEvents.length,
                              itemBuilder: (context, idx) {
                                final ev = stateEvents[idx];
                                final color = _cardColors[idx % _cardColors.length];
                                return _squarePosterCard(ev, color);
                              },
                            ),
                          ),
                      ],
                    );
                  },
                ),
                const SizedBox(height: 28),

                // 5. Section 2：所有活动的大列表 (完整的纵向 Event List)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'ALL EXPERIENCES 🎒',
                        style: TextStyle(
                          fontWeight: FontWeight.w900,
                          fontSize: 13,
                          color: Color(0xFF3D405B),
                          letterSpacing: 1.2,
                        ),
                      ),
                      Text(
                        '${filteredAllEvents.length} total',
                        style: TextStyle(fontSize: 11, color: const Color(0xFF3D405B).withValues(alpha: 0.6), fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 14),

                if (filteredAllEvents.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 30),
                    child: Center(
                      child: Text(
                        'No activities found matching "$_searchQuery"',
                        style: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.6), fontSize: 13, fontWeight: FontWeight.bold),
                      ),
                    ),
                  )
                else
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Column(
                      children: filteredAllEvents.asMap().entries.map((entry) {
                        final ev = entry.value;
                        final color = _cardColors[entry.key % _cardColors.length];
                        return _verticalEventRowItem(ev, color);
                      }).toList(),
                    ),
                  ),
              ],
            ),
          ),

          // 悬浮巡逻吉祥物
          WalkingMascot(
            onTap: _openMascotChat,
          ),
        ],
      ),
      ),
    );
  }

  // 横滑大立式卡片
  // 横滑大立式卡片
  Widget _squarePosterCard(TourismEvent ev, Color accentColor) {
    return GestureDetector(
      onTap: () => _openEventDetail(ev),
      child: Container(
        width: 235,
        margin: const EdgeInsets.only(right: 16, bottom: 8),
        decoration: BoxDecoration(
          color: Colors.transparent, // 设为透明避免底层纯白颜色干扰毛玻璃
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: accentColor.withValues(alpha: 0.28),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // 上半部海报
            Expanded(
              flex: 11,
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.network(ev.imageUrl, fit: BoxFit.cover),
                    Positioned(
                      top: 10,
                      left: 10,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: BackdropFilter(
                          filter: ImageFilter.blur(sigmaX: 4, sigmaY: 4),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            color: Colors.black.withValues(alpha: 0.55),
                            child: Text(
                              ev.category,
                              style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ),
                      ),
                    ),
                    Positioned(
                      top: 10,
                      right: 10,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: accentColor,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          ev.priceInMyr == 0 ? 'FREE' : 'RM ${ev.priceInMyr.toInt()}',
                          style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.w900),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            // 下半部信息（高斯模糊毛玻璃质感）
            Expanded(
              flex: 9,
              child: ClipRRect(
                borderRadius: const BorderRadius.vertical(bottom: Radius.circular(24)),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    padding: const EdgeInsets.fromLTRB(14, 10, 14, 10),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.65), // 半透明白底营造玻璃感
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          ev.title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15, color: Color(0xFF3D405B)),
                        ),
                        Row(
                          children: [
                            const Icon(Icons.place, size: 13, color: Color(0xFFE07A5F)),
                            const SizedBox(width: 4),
                            Expanded(
                              child: Text(
                                '${ev.address}, ${ev.state}',
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.7), fontSize: 11),
                              ),
                            ),
                          ],
                        ),
                        Row(
                          children: [
                            const Icon(Icons.access_time, size: 13, color: Colors.grey),
                            const SizedBox(width: 4),
                            Text(
                              ev.openingTime ?? 'Open daily',
                              style: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.6), fontSize: 10, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF4F1DE).withValues(alpha: 0.8),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            ev.recommendationReason,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontSize: 10,
                              fontStyle: FontStyle.italic,
                              color: Color(0xFFE07A5F),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 纵向列表行项 (展示所有存在的 Event)
  Widget _verticalEventRowItem(TourismEvent ev, Color cardColor) {
    return GestureDetector(
      onTap: () => _openEventDetail(ev),
      child: Container(
        margin: const EdgeInsets.only(bottom: 14),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: cardColor, 
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: cardColor.withValues(alpha: 0.4),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            // 缩略图
            Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(14),
                  child: Image.network(
                    ev.imageUrl,
                    width: 78,
                    height: 78,
                    fit: BoxFit.cover,
                  ),
                ),
              ],
            ),
            const SizedBox(width: 14),

            // 详情
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    ev.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    // 标题文字改成深色，适应彩色背景
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: Color(0xFF3D405B)),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${ev.address} • ${ev.state}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.75), fontSize: 11),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: const Color(0xFF3D405B),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          ev.priceInMyr == 0 ? 'FREE' : 'RM ${ev.priceInMyr.toInt()}',
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 10),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          ev.recommendationReason,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 10, color: Color(0xFF3D405B), fontStyle: FontStyle.italic, fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 6),
            const Icon(Icons.arrow_forward_ios, size: 14, color: Color(0xFF3D405B)),
          ],
        ),
      ),
    );
  }

  // 缺省状态卡片
  Widget _emptyStateCard(String state) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white, width: 1.5),
      ),
      child: Row(
        children: [
          const Icon(Icons.explore_off, size: 36, color: Color(0xFF81B29A)),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('No events listed in $state yet', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF3D405B))),
                const SizedBox(height: 2),
                const Text('Check "ALL EXPERIENCES" below or switch state in Profile.', style: TextStyle(color: Colors.black54, fontSize: 11)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// 极简淡色波点印花画笔
class _PatternPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0xFF3D405B).withValues(alpha: 0.07);
    const spacing = 30.0;
    for (double x = 0; x < size.width; x += spacing) {
      for (double y = 0; y < size.height; y += spacing) {
        final offsetX = (y / spacing) % 2 == 0 ? x : x + spacing / 2;
        canvas.drawCircle(Offset(offsetX, y), 2.5, paint);
      }
    }
  }
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}