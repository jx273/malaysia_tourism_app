import 'dart:ui';
import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import '../models/tourism_event.dart';
import 'pixel_mascot.dart';

class MascotChatSheet extends StatefulWidget {
  final TourismEvent? currentEvent;

  const MascotChatSheet({super.key, this.currentEvent});

  @override
  State<MascotChatSheet> createState() => _MascotChatSheetState();
}

class _MascotChatSheetState extends State<MascotChatSheet> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];

  @override
  void initState() {
    super.initState();
    if (widget.currentEvent != null) {
      _messages.add({
        'role': 'ai',
        'text': 'Hi! I am your guide for "${widget.currentEvent!.title}". It costs ${widget.currentEvent!.priceInMyr == 0 ? "Free Entry" : "RM ${widget.currentEvent!.priceInMyr.toInt()}"}. Ask me anything about opening hours, sustainability tips, or access!',
      });
    } else {
      _messages.add({
        'role': 'ai',
        'text': 'Hello explorer! 🐯 Tap a prompt below or ask me about green heritage spots, night markets, and local eco-adventures!',
      });
    }
  }

  void _send(String text) {
    if (text.trim().isEmpty) return;
    setState(() {
      _messages.add({'role': 'user', 'text': text});
      _messages.add({
        'role': 'ai',
        'text': widget.currentEvent != null
            ? 'Regarding "${widget.currentEvent!.title}": ${widget.currentEvent!.recommendationReason}. Operating time is ${widget.currentEvent!.openingTime ?? "09:00 AM"}. Have a wonderful visit!'
            : 'For "$text", I recommend checking out Pasar Karat JB for vibrant night culture, or Desaru Fruit Farm for family eco-tourism!',
      });
    });
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.76,
      decoration: const BoxDecoration(
        color: Color(0xFFF4F1DE),
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      child: ClipRRect(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        child: Column(
          children: [
            // 顶层抓手
            Container(
              margin: const EdgeInsets.only(top: 10, bottom: 4),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFF3D405B).withOpacity(0.2),
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // 头部毛玻璃卡片
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 8),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      border: Border.all(color: const Color(0xFFE07A5F), width: 1.5),
                    ),
                    child: ValueListenableBuilder<MascotType>(
                      valueListenable: UserSettings.instance.selectedMascot,
                      builder: (_, mascot, __) => PixelMascot(type: mascot, action: MascotAction.happy, size: 38),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.currentEvent != null ? 'Event AI Guide' : 'Ollie Companion',
                        style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16, color: Color(0xFF3D405B)),
                      ),
                      Row(
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: const BoxDecoration(color: Color(0xFF81B29A), shape: BoxShape.circle),
                          ),
                          const SizedBox(width: 4),
                          const Text(
                            'Active & Ready',
                            style: TextStyle(color: Color(0xFF81B29A), fontSize: 11, fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ],
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.close, color: Color(0xFF3D405B)),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            Divider(height: 1, color: const Color(0xFF3D405B).withOpacity(0.1)),

            // 快捷提问胶囊
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              child: Row(
                children: [
                  _chip('Free Activities 🎟️'),
                  _chip('Eco & Nature 🌿'),
                  _chip('Local Food Trail 🍜'),
                  _chip('Night Markets 🌙'),
                ],
              ),
            ),

            // 聊天消息列表
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                physics: const BouncingScrollPhysics(),
                itemCount: _messages.length,
                itemBuilder: (context, i) {
                  final isUser = _messages[i]['role'] == 'user';
                  return Align(
                    alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                    child: Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.78),
                      decoration: BoxDecoration(
                        color: isUser ? const Color(0xFFE07A5F) : Colors.white,
                        borderRadius: BorderRadius.only(
                          topLeft: const Radius.circular(18),
                          topRight: const Radius.circular(18),
                          bottomLeft: Radius.circular(isUser ? 18 : 4),
                          bottomRight: Radius.circular(isUser ? 4 : 18),
                        ),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.04),
                            blurRadius: 8,
                            offset: const Offset(0, 3),
                          ),
                        ],
                      ),
                      child: Text(
                        _messages[i]['text']!,
                        style: TextStyle(
                          color: isUser ? Colors.white : const Color(0xFF3D405B),
                          fontSize: 13,
                          height: 1.4,
                          fontWeight: isUser ? FontWeight.w600 : FontWeight.w500,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),

            // 底部输入区
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 6, 16, 14),
                child: Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(24),
                          border: Border.all(color: Colors.white, width: 1.5),
                          boxShadow: [
                            BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 8),
                          ],
                        ),
                        child: TextField(
                          controller: _controller,
                          style: const TextStyle(color: Color(0xFF3D405B), fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            hintText: 'Ask Ollie for sustainable travel tips...',
                            hintStyle: TextStyle(color: const Color(0xFF3D405B).withOpacity(0.4), fontSize: 13),
                            border: InputBorder.none,
                          ),
                          onSubmitted: _send,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      decoration: const BoxDecoration(
                        color: Color(0xFF3D405B),
                        shape: BoxShape.circle,
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.arrow_upward, color: Colors.white, size: 20),
                        onPressed: () => _send(_controller.text),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String text) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ActionChip(
        label: Text(
          text,
          style: const TextStyle(fontSize: 11, color: Color(0xFF3D405B), fontWeight: FontWeight.w800),
        ),
        backgroundColor: Colors.white.withOpacity(0.75),
        side: BorderSide(color: const Color(0xFF3D405B).withOpacity(0.15)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        onPressed: () => _send(text),
      ),
    );
  }
}