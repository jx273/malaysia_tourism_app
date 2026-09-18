import 'dart:convert';
// 注意：删掉了 dart:io，换成了下面这个
import 'package:flutter/foundation.dart'; 
import 'package:http/http.dart' as http;
import '../models/tourism_event.dart';

class ApiService {
  // 安全的跨平台判断方式
  static String get baseUrl {
    // 1. 如果在 Chrome 等网页运行
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    } 
    // 2. 如果在 Android 模拟器运行
    else if (defaultTargetPlatform == TargetPlatform.android) {
      return 'http://10.0.2.2:8000';
    } 
    // 3. iOS 模拟器或 macOS 桌面端
    else {
      return 'http://127.0.0.1:8000';
    }
  }

  // 这里的代码和你之前的一模一样
  static Future<List<TourismEvent>> fetchEvents() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/app/events'));
      
      if (response.statusCode == 200) {
        List<dynamic> body = jsonDecode(response.body);
        return body.map((dynamic item) => TourismEvent.fromJson(item)).toList();
      } else {
        throw Exception('连接后端失败: 状态码 ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('网络连不上，报错信息: $e'); 
    }
  }

    // 2. 获取 AI 智能推荐 (POST 请求)
  static Future<List<Map<String, dynamic>>> getAiRecommendations({
    required double lat,
    required double lng,
    required List<String> interests,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/legacy/recommend'),
        headers: {'Content-Type': 'application/json'},
        // 把用户的当前位置和兴趣打包成 JSON 发给后端
        body: jsonEncode({
          'lat': lat,
          'lng': lng,
          'travel_date': DateTime.now().toIso8601String().split('T')[0], // 默认今天
          'interests': interests,
        }),
      );

      if (response.statusCode == 200) {
        // 请求成功，解析返回的 JSON 数据
        List<dynamic> body = jsonDecode(response.body);
        
        // 返回一个包含 name 和 match_score 的字典列表
        return List<Map<String, dynamic>>.from(body);
      } else {
        throw Exception('AI 推荐接口报错: 状态码 ${response.statusCode}');
      }
    } catch (e) {
      print('AI 推荐接口连接失败: $e');
      return []; // 报错时返回空列表防崩溃
    }
  }

}
