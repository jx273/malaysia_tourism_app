import 'dart:ui';
import 'package:flutter/material.dart';
import '../data/user_settings.dart';
import '../widgets/pixel_mascot.dart';

class AuthScreen extends StatefulWidget {
  final bool initialIsLogin;
  const AuthScreen({super.key, this.initialIsLogin = true});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  late bool _isLogin;
  final _nameController = TextEditingController();
  final _pwdFocus = FocusNode();
  bool _isPasswordFocused = false;
  bool _obscureText = true;

  @override
  void initState() {
    super.initState();
    _isLogin = widget.initialIsLogin;
    _pwdFocus.addListener(() {
      setState(() => _isPasswordFocused = _pwdFocus.hasFocus);
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    _pwdFocus.dispose();
    super.dispose();
  }

  void _submit() {
    final settings = UserSettings.instance;
    if (!_isLogin && _nameController.text.trim().isNotEmpty) {
      settings.userName.value = _nameController.text.trim();
    }
    // 触发登录状态变更，main.dart 会自动将页面切换为 Home
    settings.isLoggedIn.value = true;
    
    // 如果是从 Profile 作为访客点进来的，登录后把当前页面 Pop 掉
    if (Navigator.canPop(context)) {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    final mascotType = UserSettings.instance.selectedMascot.value;
    MascotAction currentAction = _isPasswordFocused ? MascotAction.coverEyes : MascotAction.idleFront;
    
    return Scaffold(
      backgroundColor: const Color(0xFFF4F1DE),
      body: Stack(
        children: [
          // 全局淡色印花背景
          Positioned.fill(child: CustomPaint(painter: _PatternPainter())),
          
          Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: ConstrainedBox(
                // 限制最大宽度，保证在电脑网页端表单依旧精致小巧
                constraints: const BoxConstraints(maxWidth: 400),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // 若能返回（例如访客模式点进来的），显示关闭按钮
                    if (Navigator.canPop(context))
                      Align(
                        alignment: Alignment.topLeft,
                        child: IconButton(
                          icon: const Icon(Icons.close, color: Color(0xFF3D405B)),
                          onPressed: () => Navigator.pop(context),
                        ),
                      ),
                    
                    // 顶部吉祥物
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        border: Border.all(color: const Color(0xFFE07A5F), width: 2),
                        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 15, offset: const Offset(0, 4))],
                      ),
                      child: PixelMascot(type: mascotType, action: currentAction, size: 65),
                    ),
                    const SizedBox(height: 24),
                    
                    Text(
                      _isLogin ? 'Welcome Back!' : 'Join JalanJalan',
                      style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, color: Color(0xFF3D405B), letterSpacing: -0.5),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _isLogin ? 'Sign in to access your itinerary and memories' : 'Create an account to explore local experiences',
                      style: TextStyle(fontSize: 13, color: Colors.grey.shade600, fontWeight: FontWeight.w500),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),

                    // 核心：玻璃态 (Glassmorphism) 表单框
                    ClipRRect(
                      borderRadius: BorderRadius.circular(28),
                      child: BackdropFilter(
                        filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
                        child: Container(
                          padding: const EdgeInsets.all(28),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.65), // 苹果质感半透明白
                            borderRadius: BorderRadius.circular(28),
                            border: Border.all(color: Colors.white.withOpacity(0.9), width: 1.5),
                            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 24, offset: const Offset(0, 10))],
                          ),
                          child: Column(
                            children: [
                              if (!_isLogin) ...[
                                _buildTextField(Icons.person_outline, 'Full Name', controller: _nameController),
                                const SizedBox(height: 16),
                              ],
                              _buildTextField(Icons.email_outlined, 'Email Address'),
                              const SizedBox(height: 16),
                              _buildTextField(Icons.lock_outline, 'Password', isPassword: true, focusNode: _pwdFocus),
                              const SizedBox(height: 32),
                              
                              // 珊瑚红渐变按钮
                              SizedBox(
                                width: double.infinity,
                                height: 52,
                                child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFFE07A5F), // 彻底告别深绿色
                                    foregroundColor: Colors.white,
                                    shadowColor: const Color(0xFFE07A5F).withOpacity(0.5),
                                    elevation: 8,
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                  ),
                                  onPressed: _submit,
                                  child: Text(_isLogin ? 'Sign In' : 'Create Account', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900, letterSpacing: 0.5)),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 28),
                    
                    TextButton(
                      onPressed: () => setState(() => _isLogin = !_isLogin),
                      child: RichText(
                        text: TextSpan(
                          text: _isLogin ? "Don't have an account? " : "Already have an account? ",
                          style: TextStyle(color: Colors.grey.shade600, fontSize: 13, fontWeight: FontWeight.w600),
                          children: [
                            TextSpan(text: _isLogin ? 'Register' : 'Sign In', style: const TextStyle(color: Color(0xFFE07A5F), fontWeight: FontWeight.w900)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField(IconData icon, String hint, {bool isPassword = false, FocusNode? focusNode, TextEditingController? controller}) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white, width: 2),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 4, offset: const Offset(0, 2))],
      ),
      child: TextField(
        controller: controller,
        focusNode: focusNode,
        obscureText: isPassword && _obscureText,
        style: const TextStyle(fontSize: 14, color: Color(0xFF3D405B), fontWeight: FontWeight.w700),
        decoration: InputDecoration(
          prefixIcon: Icon(icon, color: const Color(0xFF81B29A), size: 20), // 用薄荷绿代替原有的深绿
          suffixIcon: isPassword
              ? IconButton(
                  icon: Icon(_obscureText ? Icons.visibility_off_outlined : Icons.visibility_outlined, color: Colors.grey.shade400, size: 20),
                  onPressed: () => setState(() => _obscureText = !_obscureText),
                )
              : null,
          hintText: hint,
          hintStyle: TextStyle(color: Colors.grey.shade400, fontSize: 13, fontWeight: FontWeight.w500),
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
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