// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:foodlens_ai/main.dart';
import 'package:foodlens_ai/shared/utils/performance_helper.dart';

void main() {
  group('Performance Optimizations Tests', () {
    testWidgets('PerformanceHelper initializes correctly', (WidgetTester tester) async {
      // Test that PerformanceHelper can be initialized without issues
      await PerformanceHelper.init();
      
      // Check that the helper provides consistent responses
      expect(PerformanceHelper.isLowEndDevice, isA<bool>());
      expect(PerformanceHelper.shouldUseAnimations, isA<bool>());
      expect(PerformanceHelper.shouldUseComplexAnimations, isA<bool>());
      expect(PerformanceHelper.targetFrameRate, isA<int>());
    });

    testWidgets('Animation durations are optimized for low-end devices', (WidgetTester tester) async {
      await PerformanceHelper.init();
      
      const originalDuration = Duration(milliseconds: 1000);
      final optimizedDuration = PerformanceHelper.getAnimationDuration(originalDuration);
      
      // Duration should be either the same or reduced
      expect(optimizedDuration.inMilliseconds <= originalDuration.inMilliseconds, isTrue);
      
      if (PerformanceHelper.isLowEndDevice) {
        // For low-end devices, duration should be reduced
        expect(optimizedDuration.inMilliseconds < originalDuration.inMilliseconds, isTrue);
      }
    });

    testWidgets('Main app launches without memory issues', (WidgetTester tester) async {
      // This test verifies that the app can launch with our optimizations
      // Build our app and trigger a frame.
      await tester.pumpWidget(const FoodLensApp());

      // Wait for initialization
      await tester.pumpAndSettle();

      // Verify that the app builds successfully (no memory crashes)
      expect(find.byType(MaterialApp), findsOneWidget);
    });

    test('Performance helper provides safe defaults', () async {
      await PerformanceHelper.init();
      
      // Test that all methods return safe values
      expect(PerformanceHelper.targetFrameRate, greaterThan(0));
      expect(PerformanceHelper.targetFrameRate, lessThanOrEqualTo(60));
      expect(PerformanceHelper.imageCacheLimitMB, greaterThan(0));
      expect(PerformanceHelper.getOptimizedListItemCount(100), greaterThan(0));
    });
  });
}
