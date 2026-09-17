import 'package:flutter/foundation.dart';
import '../widgets/pixel_mascot.dart';

class UserSettings {
  static final UserSettings instance = UserSettings._internal();
  UserSettings._internal();

// 新增所在州属状态，默认 Johor
  final ValueNotifier<String> selectedState = ValueNotifier<String>('Johor');
  
  // DOSM 官方规范的 16 个州属/直辖区
  final List<String> states = [
    'Johor', 'Kedah', 'Kelantan', 'Melaka', 'Negeri Sembilan', 'Pahang',
    'Pulau Pinang', 'Perak', 'Perlis', 'Selangor', 'Terengganu', 'Sabah',
    'Sarawak', 'W.P. Kuala Lumpur', 'W.P. Labuan', 'W.P. Putrajaya'
  ];

  final ValueNotifier<MascotType> selectedMascot =
      ValueNotifier<MascotType>(MascotType.tiger);

  final ValueNotifier<bool> isLoggedIn = ValueNotifier<bool>(true);
  final ValueNotifier<String> userName = ValueNotifier<String>('JiaXuan');

  void switchMascot(MascotType type) {
    selectedMascot.value = type;
  }

  void toggleLogin() {
    isLoggedIn.value = !isLoggedIn.value;
  }
}