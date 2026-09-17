import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import '../widgets/pixel_mascot.dart';
import 'auth_screen.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = UserSettings.instance;

    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      appBar: AppBar(
        title: const Text('Profile & Preferences', style: TextStyle(color: Color(0xFF3D405B), fontWeight: FontWeight.w900, fontSize: 20)),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Stack(
        children: [
          // 底层全局印花
          Positioned.fill(child: CustomPaint(painter: _PatternPainter())),
          
          ListView(
            padding: const EdgeInsets.fromLTRB(20, 10, 20, 120),
            physics: const BouncingScrollPhysics(),
            children: [
              // 1. 吉祥物选择
              const Text('Companion Mascot', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: Color(0xFF3D405B))),
              const SizedBox(height: 12),
              ValueListenableBuilder<MascotType>(
                valueListenable: settings.selectedMascot,
                builder: (_, mascot, __) => Row(
                  children: [
                    _mascotCard(
                      title: 'Malayan Tiger',
                      type: MascotType.tiger,
                      selected: mascot == MascotType.tiger,
                      onTap: () => settings.selectedMascot.value = MascotType.tiger,
                    ),
                    const SizedBox(width: 16),
                    _mascotCard(
                      title: 'Malayan Tapir',
                      type: MascotType.tapir,
                      selected: mascot == MascotType.tapir,
                      onTap: () => settings.selectedMascot.value = MascotType.tapir,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // 2. 偏好设置 (带 Icon 的横向布局列)
              const Text('Preferences', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: Color(0xFF3D405B))),
              const SizedBox(height: 12),
              Container(
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.85),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.white, width: 1.5),
                  boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))],
                ),
                child: Column(
                  children: [
                    // Location 选择器
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      child: Row(
                        children: [
                          const Icon(Icons.location_on_rounded, color: Color(0xFFE07A5F), size: 22),
                          const SizedBox(width: 14),
                          const Text('My Location', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF3D405B))),
                          const Spacer(),
                          ValueListenableBuilder<String>(
                            valueListenable: settings.selectedState,
                            builder: (_, currentState, __) => DropdownButtonHideUnderline(
                              child: DropdownButton<String>(
                                value: currentState,
                                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Color(0xFF3D405B)),
                                style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFE07A5F), fontSize: 13),
                                items: settings.states.map((state) => DropdownMenuItem(value: state, child: Text(state))).toList(),
                                onChanged: (val) {
                                  if (val != null) settings.selectedState.value = val;
                                },
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Divider(height: 1, color: Colors.grey.shade200, indent: 52),
                    // Language
                    _settingsRow(Icons.language_rounded, 'Language', 'English (Default)', const Color(0xFF81B29A)),
                    Divider(height: 1, color: Colors.grey.shade200, indent: 52),
                    // Notification (模拟项，让界面更丰满)
                    _settingsRow(Icons.notifications_active_rounded, 'Notifications', 'Enabled', const Color(0xFFF2CC8F)),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // 3. 账户操作区 (极简登录/登出)
              const Text('Account', style: TextStyle(fontWeight: FontWeight.w900, fontSize: 14, color: Color(0xFF3D405B))),
              const SizedBox(height: 12),
              ValueListenableBuilder<bool>(
                valueListenable: settings.isLoggedIn,
                builder: (_, loggedIn, __) => ValueListenableBuilder<String>(
                  valueListenable: settings.userName,
                  builder: (_, name, __) => Container(
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.85),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.white, width: 1.5),
                      boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 10, offset: const Offset(0, 4))],
                    ),
                    child: ListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                      leading: CircleAvatar(
                        backgroundColor: const Color(0xFF3D405B).withOpacity(0.1),
                        child: const Icon(Icons.person_rounded, color: Color(0xFF3D405B)),
                      ),
                      title: Text(loggedIn ? name : 'Guest Explorer', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 15, color: Color(0xFF3D405B))),
                      subtitle: Text(loggedIn ? 'Member' : 'Tap to sign in', style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                      trailing: TextButton(
                        style: TextButton.styleFrom(
                          backgroundColor: loggedIn ? Colors.red.shade50 : const Color(0xFFE07A5F).withOpacity(0.1),
                          foregroundColor: loggedIn ? Colors.redAccent : const Color(0xFFE07A5F),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        onPressed: () {
                          if (loggedIn) {
                            settings.isLoggedIn.value = false;
                          } else {
                            Navigator.push(context, MaterialPageRoute(builder: (_) => const AuthScreen(initialIsLogin: true)));
                          }
                        },
                        child: Text(loggedIn ? 'Log Out' : 'Sign In', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 48),

              // 4. 底部版权与版本号
              Center(
                child: Column(
                  children: [
                    const Text('Version 1.0', style: TextStyle(color: Colors.black38, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.5)),
                    const SizedBox(height: 6),
                    Text('Made by Group: 404 Not Found', style: TextStyle(color: const Color(0xFF3D405B).withOpacity(0.4), fontSize: 11, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _settingsRow(IconData icon, String title, String trailingText, Color iconColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      child: Row(
        children: [
          Icon(icon, color: iconColor, size: 22),
          const SizedBox(width: 14),
          Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFF3D405B))),
          const Spacer(),
          Text(trailingText, style: TextStyle(color: Colors.grey.shade500, fontSize: 12, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _mascotCard({required String title, required MascotType type, required bool selected, required VoidCallback onTap}) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: selected ? Colors.white : Colors.white.withOpacity(0.5),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: selected ? const Color(0xFFE07A5F) : Colors.white, width: selected ? 2.5 : 1.5),
            boxShadow: [
              if (selected) BoxShadow(color: const Color(0xFFE07A5F).withOpacity(0.15), blurRadius: 15, offset: const Offset(0, 6)),
            ],
          ),
          child: Column(
            children: [
              PixelMascot(type: type, action: selected ? MascotAction.happy : MascotAction.idleFront, size: 45),
              const SizedBox(height: 10),
              Text(title, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w900, color: selected ? const Color(0xFFE07A5F) : const Color(0xFF3D405B))),
            ],
          ),
        ),
      ),
    );
  }
}

class _PatternPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0xFF3D405B).withOpacity(0.07);
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