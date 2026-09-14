import 'package:flutter/foundation.dart';
import '../widgets/pixel_mascot.dart';

class UserSettings {
  static final UserSettings instance = UserSettings._internal();
  UserSettings._internal();

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