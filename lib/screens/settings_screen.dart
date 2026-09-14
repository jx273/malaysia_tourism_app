import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import '../widgets/pixel_mascot.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = UserSettings.instance;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          'Settings & Profile',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 500),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ValueListenableBuilder<bool>(
                valueListenable: settings.isLoggedIn,
                builder: (context, isLoggedIn, _) {
                  return Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.grey.shade200),
                    ),
                    child: Row(
                      children: [
                        CircleAvatar(
                          radius: 26,
                          backgroundColor: const Color(0xFF007A3D).withOpacity(0.15),
                          child: Icon(
                            isLoggedIn ? Icons.person : Icons.person_outline,
                            color: const Color(0xFF007A3D),
                            size: 28,
                          ),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isLoggedIn ? settings.userName.value : 'Guest Explorer',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                isLoggedIn
                                    ? 'Member • Cultural Explorer'
                                    : 'Log in to sync your itinerary',
                                style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
                              ),
                            ],
                          ),
                        ),
                        OutlinedButton(
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: isLoggedIn ? Colors.redAccent : const Color(0xFF007A3D),
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10),
                            ),
                          ),
                          onPressed: () {
                            settings.toggleLogin();
                          },
                          child: Text(
                            isLoggedIn ? 'Log Out' : 'Sign In',
                            style: TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: isLoggedIn ? Colors.redAccent : const Color(0xFF007A3D),
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),

              const SizedBox(height: 24),

              const Text(
                'AI COMPANION MASCOT',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: Color(0xFF64748B),
                ),
              ),
              const SizedBox(height: 10),

              ValueListenableBuilder<MascotType>(
                valueListenable: settings.selectedMascot,
                builder: (context, currentMascot, _) {
                  return Row(
                    children: [
                      Expanded(
                        child: GestureDetector(
                          onTap: () => settings.switchMascot(MascotType.tiger),
                          child: Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: currentMascot == MascotType.tiger
                                    ? const Color(0xFF007A3D)
                                    : Colors.grey.shade200,
                                width: currentMascot == MascotType.tiger ? 2 : 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                const PixelMascot(
                                  type: MascotType.tiger,
                                  action: MascotAction.idleFront,
                                  size: 48,
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  'Tiger Cub (Default)',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                if (currentMascot == MascotType.tiger)
                                  const Icon(Icons.check_circle, color: Color(0xFF007A3D), size: 18),
                              ],
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),

                      Expanded(
                        child: GestureDetector(
                          onTap: () => settings.switchMascot(MascotType.tapir),
                          child: Container(
                            padding: const EdgeInsets.all(14),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: currentMascot == MascotType.tapir
                                    ? const Color(0xFF007A3D)
                                    : Colors.grey.shade200,
                                width: currentMascot == MascotType.tapir ? 2 : 1,
                              ),
                            ),
                            child: Column(
                              children: [
                                const PixelMascot(
                                  type: MascotType.tapir,
                                  action: MascotAction.idleFront,
                                  size: 48,
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  'Malayan Tapir',
                                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                if (currentMascot == MascotType.tapir)
                                  const Icon(Icons.check_circle, color: Color(0xFF007A3D), size: 18),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),

              const SizedBox(height: 24),

              const Text(
                'PREFERENCES',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.0,
                  color: Color(0xFF64748B),
                ),
              ),
              const SizedBox(height: 10),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey.shade200),
                ),
                child: Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.language, color: Color(0xFF007A3D), size: 20),
                      title: const Text('Language', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      trailing: const Text('English (MY)', style: TextStyle(fontSize: 12, color: Colors.grey)),
                      onTap: () {},
                    ),
                    Divider(height: 1, color: Colors.grey.shade100),
                    ListTile(
                      leading: const Icon(Icons.notifications_none, color: Color(0xFF007A3D), size: 20),
                      title: const Text('Event Alerts', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      trailing: Switch(
                        value: true,
                        activeColor: const Color(0xFF007A3D),
                        onChanged: (val) {},
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}