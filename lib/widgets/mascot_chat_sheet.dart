import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';          
import 'package:google_generative_ai/google_generative_ai.dart'; 
import '../services/api_service.dart';
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

      void _send(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _messages.add({'role': 'user', 'text': text});
      _messages.add({'role': 'ai', 'text': 'Ollie is thinking... 🐯💭'});
    });
    _controller.clear();

    try {
      final apiKey = dotenv.env['GEMINI_API_KEY'];
      if (apiKey == null) throw Exception('API Key not found in .env');
      
      final model = GenerativeModel(model: 'gemini-3.1-flash-lite', apiKey: apiKey);

      if (widget.currentEvent == null) {
        // To detect greetings, use a regex to match common greeting phrases.
        final isGreeting = RegExp(r'^(hi|hello|hey|how are you|你好|早安|午安)', caseSensitive: false).hasMatch(text.trim());

        String prompt;

        if (isGreeting) {
          prompt = '''
          You are Ollie, a friendly, warm tiger mascot for the JalanJalan sustainable tourism app in Malaysia.
          The user just greeted you with: "$text".
          Respond politely, introduce yourself briefly in 1-2 friendly sentences, and ask how you can help them explore Malaysia sustainably.
          Use 1 cute emoji.
          ''';
        } else {
          // Remove emojis and special characters to extract the main interest keyword
          String interest = text.replaceAll(RegExp(r'[^\w\s]'), '').trim();

          final results = await ApiService.getAiRecommendations(
            lat: 1.45,
            lng: 103.76,
            interests: [interest.isEmpty ? 'General' : interest],
          );

          // Create a summary of candidates for the prompt
          String candidatesSummary = results.map((e) {
            return "- ${e['name']} (Match Score: ${((e['match_score'] ?? 0) * 100).toInt()}%)";
          }).join("\n");

          prompt = '''
          You are Ollie, an eco-conscious tiger mascot for a Malaysia travel app.
          User input: "$text".
          
          Here are available destination options evaluated by our backend data model:
          $candidatesSummary
          
          Instructions:
          1. Pick the destination that BEST fits the user's category (e.g. if Nature, pick Farm or Firefly, NOT Night Market).
          2. Explain in 2 sentences why it's worth visiting and how it helps avoid tourist overcrowding.
          3. Mention the match score. Keep the tone fun and encouraging.
          ''';
        }

        final response = await model.generateContent([Content.text(prompt)]);

        setState(() {
          _messages.removeLast();
          _messages.add({'role': 'ai', 'text': response.text ?? 'Roar! How can I help you explore?'});
        });

      } else {
        // Detail page logic: single Q&A for the currently selected event
        final prompt = '''
        You are Ollie, a travel companion. The user is browsing "${widget.currentEvent!.title}".
        Location: ${widget.currentEvent!.address ?? 'Johor'}
        Price: RM ${widget.currentEvent!.priceInMyr.toInt()}
        Hours: ${widget.currentEvent!.openingTime ?? '09:00'} - ${widget.currentEvent!.closingTime ?? '22:00'}
        Summary: ${widget.currentEvent!.description}

        User inquiry: "$text".
        Reply concisely in 1-2 sentences using this context.
        ''';

        final response = await model.generateContent([Content.text(prompt)]);

        setState(() {
          _messages.removeLast();
          _messages.add({'role': 'ai', 'text': response.text ?? 'Have a wonderful visit!'});
        });
      }
    } catch (e) {
      setState(() {
        _messages.removeLast();
        _messages.add({'role': 'ai', 'text': 'Oops, Ollie is taking a quick nap! 🐯💤 ($e)'});
      });
    }
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
            Container(
              margin: const EdgeInsets.only(top: 10, bottom: 4),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: const Color(0xFF3D405B).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(2),
              ),
            ),

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
                      builder: (_, mascot, _) => PixelMascot(type: mascot, action: MascotAction.happy, size: 38),
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
            Divider(height: 1, color: const Color(0xFF3D405B).withValues(alpha: 0.1)),

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
                            color: Colors.black.withValues(alpha: 0.04),
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
                            BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 8),
                          ],
                        ),
                        child: TextField(
                          controller: _controller,
                          style: const TextStyle(color: Color(0xFF3D405B), fontSize: 14, fontWeight: FontWeight.w600),
                          decoration: InputDecoration(
                            hintText: 'Ask Ollie for sustainable travel tips...',
                            hintStyle: TextStyle(color: const Color(0xFF3D405B).withValues(alpha: 0.4), fontSize: 13),
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
        backgroundColor: Colors.white.withValues(alpha: 0.75),
        side: BorderSide(color: const Color(0xFF3D405B).withValues(alpha: 0.15)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        onPressed: () => _send(text),
      ),
    );
  }
}