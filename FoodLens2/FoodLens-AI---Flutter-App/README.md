<<<<<<< HEAD
# 🍎 FoodLens AI - Your Smart Food Transparency Companion

<div align="center">

[![Flutter](https://img.shields.io/badge/Flutter-3.19%2B-02569B?logo=flutter)](https://flutter.dev)
[![Dart](https://img.shields.io/badge/Dart-3.3%2B-0175C2?logo=dart)](https://dart.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Making Food Choices Smarter, Healthier, and More Transparent**

[Features](#-features) • [Installation](#-installation--setup) • [Usage](#-testing-the-app) • [Backend Integration](#-backend-integration-guide) • [Contributing](#-contributing)

</div>

---

## 📑 Table of Contents

- [📖 What is FoodLens AI?](#-what-is-foodlens-ai)
  - [🎯 What Does FoodLens AI Do?](#-what-does-foodlens-ai-do)
  - [🌟 Why FoodLens AI?](#-why-foodlens-ai)
- [🏗 Architecture Overview](#-architecture-overview)
- [🚨 VS Code Crash Prevention](#-vs-code-crash-prevention)
- [🚀 Features](#-features)
- [📦 Installation & Setup](#-installation--setup)
- [🏗 Project Structure](#-project-structure)
- [📸 App Screenshots & Demo](#-app-screenshots--demo)
- [🧪 Testing the App](#-testing-the-app)
- [🔧 Development Commands](#-development-commands)
- [📱 Building for Release](#-building-for-release)
- [🔌 Backend Integration Guide](#-backend-integration-guide)
- [🎯 Next Steps & Roadmap](#-next-steps--roadmap)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📞 Support & Resources](#-support--resources)
- [📄 License](#-license)

---

## 📖 What is FoodLens AI?

**FoodLens AI** is a cutting-edge mobile application that empowers users to make informed food choices by providing instant, AI-powered nutritional analysis of any food product. Simply scan a barcode or take a photo of a nutrition label, and FoodLens AI delivers personalized health insights tailored to your dietary needs and health goals.

### 🎯 What Does FoodLens AI Do?

FoodLens AI transforms the way you understand food by:

- **🔍 Instant Food Analysis**: Scan any product barcode or nutrition label to get comprehensive nutritional information
- **🤖 AI-Powered Insights**: Receive personalized health recommendations based on your unique health profile, dietary goals, and allergies
- **⚠️ Smart Warnings**: Get alerted about ingredients that may conflict with your health conditions (diabetes, hypertension, allergies, etc.)
- **💚 Health Scoring**: See at-a-glance health scores for products based on nutritional value and ingredient quality
- **🔄 Better Alternatives**: Discover healthier alternatives to products that don't align with your health goals
- **📊 Nutrition Tracking**: Track your food scan history and monitor your dietary patterns over time
- **💬 AI Chatbot**: Ask questions about nutrition, ingredients, and get personalized dietary advice
- **📝 Food Blog**: Stay informed with articles about nutrition, health tips, and food trends

### 🌟 Why FoodLens AI?

In a world where food labels can be confusing and nutritional information overwhelming, FoodLens AI acts as your personal nutritionist in your pocket. Whether you're managing a health condition, working towards fitness goals, or simply want to eat healthier, FoodLens AI makes understanding food effortless.

**Perfect For:**
- 🏃 Fitness enthusiasts tracking macros and calories
- 💊 Individuals managing health conditions (diabetes, heart disease, etc.)
- 🚫 People with food allergies or dietary restrictions
- 🥗 Anyone pursuing specific dietary goals (weight loss, muscle gain, clean eating)
- 👨‍👩‍👧‍👦 Parents making healthier choices for their families
- 🌱 Conscious consumers seeking transparency in food products

---

## 🏗 Architecture Overview

FoodLens AI is built as a premium Flutter frontend with seamless integration points for an Agentic AI backend system. The app features:

- **Material 3 Design System** with custom color palette and advanced animations
- **Modular Architecture** with clear separation of concerns
- **Riverpod State Management** for reactive and maintainable code
- **Mock Data System** allowing frontend development independent of backend
- **Comprehensive API Integration Layer** ready for production backend connection

## 🚨 **VS Code Crash Prevention** 

**CRITICAL**: If you experience VS Code crashes, especially when using GitHub Copilot, or "This window is not responding" messages:

1. **🚑 Emergency Performance Mode** (For severe lagging/hanging):
   ```bash
   # Run the performance fix script
   ./scripts/fix_vscode_performance.sh
   
   # Then in VS Code: Run > Start Debugging > "Flutter (Emergency Performance Mode)"
   ```

2. **Use the Ultra-Safe Copilot Configuration** (Recommended for 4GB RAM systems):
   ```bash
   # In VS Code: Run > Start Debugging > "Flutter (Copilot Safe - Ultra Minimal)"
   # Or use the task: "Flutter: Run (Copilot Safe - Ultra Minimal)"
   ```

3. **Use the Workspace File** (General crash prevention):
   ```bash
   # Open this file in VS Code instead of the folder
   FoodLens-AI.code-workspace
   ```

4. **Emergency Recovery**: If VS Code is completely unresponsive, see [EMERGENCY_RECOVERY.md](EMERGENCY_RECOVERY.md)

5. **Alternative**: Follow the comprehensive guide at [VS_CODE_CRASH_PREVENTION.md](VS_CODE_CRASH_PREVENTION.md)

6. **For GitHub Copilot Users**: 
   - Use the "Flutter (Copilot Safe - Ultra Minimal)" launch configuration
   - Limit Copilot suggestions to Dart files only (automatically configured)
   - Memory monitoring widget shows live memory usage in debug mode
   - Automatic cleanup runs every 30 seconds on low-memory systems

7. **Performance Fix Script**: 
   ```bash
   # Run the automated performance fix for lagging VS Code
   ./scripts/fix_vscode_performance.sh
   ```

8. **Validation Script**: 
   ```bash
   # Run the validation script to check your configuration
   ./scripts/validate_copilot_config.sh
   ```

---

## 🚀 Features

### 🔍 **Smart Food Scanning**
- **Dual Scanning Modes**: 
  - 📊 **Barcode Scanner**: Instantly identify products by scanning barcodes
  - 📸 **Photo Scanner**: Capture nutrition labels with OCR technology
- **Real-time Processing**: Get instant analysis results powered by AI
- **Comprehensive Database**: Access nutritional information for thousands of products
- **Offline Capability**: View previously scanned items without internet

### 🤖 **AI-Powered Analysis**
- **Personalized Health Scoring**: Products rated based on YOUR health profile
- **Ingredient Deep-Dive**: Understand every ingredient and its health impact
- **Allergen Detection**: Automatic warnings for allergens matching your profile
- **Nutrition Breakdown**: Detailed macros, micros, and daily value percentages
- **Processing Level Assessment**: Know if food is ultra-processed, processed, or whole
- **Claims Verification**: AI validates marketing claims like "organic" or "all-natural"

### 💚 **Personalized Health Management**
- **Custom Health Profiles**: 
  - Set dietary goals (weight loss, muscle gain, maintenance)
  - Track health conditions (diabetes, hypertension, cholesterol, etc.)
  - Register allergies and food sensitivities
  - Define activity levels and caloric needs
- **Smart Recommendations**: 
  - Get product alternatives that better match your goals
  - Receive personalized dietary coaching
  - Track progress towards health objectives
- **Nutrition Insights**: View trends in your eating habits over time

### 📱 **Core App Features**

#### 🏠 **Home Dashboard**
- Personalized greeting and daily health summary
- Quick access to scanning and recent analyses
- Health score trends and statistics
- Featured articles and nutrition tips

#### 🔐 **Secure Authentication**
- Multi-step signup with health questionnaire
- Social login (Google, Apple, Facebook)
- Biometric authentication support
- Secure password management

#### 📊 **Scan History**
- Complete history of analyzed products
- Search and filter your scans
- Track nutritional patterns
- Export data for external analysis

#### 💬 **AI Nutrition Chatbot**
- Ask questions about specific foods
- Get instant nutritional advice
- Understand complex ingredients
- Receive personalized tips based on your profile

#### 📝 **Food & Health Blog**
- Expert articles on nutrition and wellness
- Latest food industry news
- Healthy recipes and meal ideas
- Community tips and success stories

#### ⭐ **Favorites & Collections**
- Save products you love
- Create custom food collections
- Quick access to frequently consumed items
- Share favorites with friends

#### 🔎 **Advanced Search**
- Search products by name or brand
- Filter by nutritional criteria
- Find alternatives to specific products
- Browse by category or dietary preference

#### 👤 **Profile Management**
- Update health information anytime
- Manage dietary preferences
- Set goals and track progress
- Customize app settings and notifications

### 🎨 **Premium UI/UX**
- **Material 3 Design** with custom color palette and typography
- **Dark/Light Theme Support** with smooth transitions
- **Advanced Animations** using flutter_animate, lottie, and staggered animations
- **Glassmorphism Effects** and gradient cards
- **Responsive Design** for all screen sizes and devices
- **Accessibility Features** for inclusive user experience

### 🛠 **Technical Excellence**
- **Flutter 3.19+** with null safety
- **Riverpod** for robust state management
- **GoRouter** for type-safe navigation with guards
- **Firebase Integration** for authentication and cloud services
- **Secure Storage** for sensitive data
- **Permission Handling** for camera and storage access
- **Network Resilience** with offline support
- **Performance Optimized** for devices with 4GB RAM
- **Memory Monitoring** tools for development

## 📦 Installation & Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Flutter SDK** (3.19 or higher) - [Install Flutter](https://docs.flutter.dev/get-started/install)
- **Dart SDK** (3.3 or higher) - Comes with Flutter
- **IDE**: Android Studio, VS Code, or IntelliJ IDEA
- **Git** - [Install Git](https://git-scm.com/downloads)
- **Platform-specific tools**:
  - For Android: Android Studio and Android SDK
  - For iOS: Xcode (macOS only) and CocoaPods

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/mohitkattungal/FoodLens-AI---Flutter-App.git

# Navigate to the project directory
cd FoodLens-AI---Flutter-App

# Install dependencies
flutter pub get
```

### 2. Verify Flutter Installation

```bash
# Check Flutter installation and dependencies
flutter doctor

# Accept Android licenses (if needed)
flutter doctor --android-licenses
```

### 3. Configure Firebase (Optional - for full authentication)

If you want to use Firebase authentication:

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Add your Android/iOS app to the Firebase project
3. Download `google-services.json` (Android) and `GoogleService-Info.plist` (iOS)
4. Place them in the appropriate directories:
   - Android: `android/app/google-services.json`
   - iOS: `ios/Runner/GoogleService-Info.plist`

> **Note**: The app works with mock authentication in development mode without Firebase configuration.

### 4. Run the App

```bash
# List available devices
flutter devices

# Run on connected device/emulator
flutter run

# Run in debug mode with hot reload
flutter run --debug

# Run on specific device
flutter run -d <device-id>
```

### 5. Platform-Specific Setup

#### Android

```bash
# Create debug APK
flutter build apk --debug

# Run on Android emulator
flutter emulators --launch <emulator-id>
flutter run
```

#### iOS (macOS only)

```bash
# Navigate to iOS folder and install dependencies
cd ios
pod install
cd ..

# Run on iOS simulator
open -a Simulator
flutter run

# Build for iOS
flutter build ios --debug
```

### 6. Development Mode

The app includes a **development mode** that allows you to test all features without a backend:

- Authentication works with mock users
- Food analysis shows sample data
- All UI components are fully functional
- Perfect for frontend development and testing

To enable production mode, update the `kDevelopmentMode` flag in `lib/shared/providers/auth_provider.dart`.

## 🏗 **Project Structure**

```
lib/
├── core/
│   ├── constants/           # App colors, typography, sizes
│   ├── theme/              # Theme configuration
│   └── router/             # Navigation setup
├── shared/
│   ├── providers/          # Riverpod state management
│   ├── models/            # Data models
│   ├── widgets/           # Reusable components
│   └── services/          # API integration layer
├── features/
│   ├── welcome/           # Onboarding screens
│   ├── auth/              # Login/signup
│   ├── home/              # Dashboard
│   ├── scan/              # Camera interface
│   ├── profile/           # User management
│   └── analysis/          # Food analysis details
└── main.dart              # App entry point

assets/
├── fonts/                 # Custom typography
├── images/                # App icons, logos
├── animations/            # Lottie files
└── icons/                 # Custom icons
```

## 🔌 Backend Integration Guide

FoodLens AI is designed with a clean separation between frontend and backend, making integration straightforward. The app includes clearly marked integration points and mock data structures that match the expected API responses.

### 📋 Integration Overview

The app requires a backend system that provides:

- **🤖 Agentic AI Analysis**: Food recognition, nutritional analysis, and personalized recommendations
- **👤 User Management**: Authentication, profiles, and health questionnaires
- **📊 Data Storage**: Scan history, favorites, and user preferences
- **💬 Chatbot**: Conversational AI for nutrition advice
- **📝 Content**: Blog articles and nutrition tips

### 🔗 Required API Endpoints

#### 🤖 **Agentic AI System**

```http
POST   /api/scan/barcode              # Process barcode scan
POST   /api/scan/photo                # Process photo with OCR
GET    /api/analysis/{analysisId}     # Get detailed AI analysis
GET    /api/food/{id}/alternatives    # Get healthier alternatives
POST   /api/chat/message              # Send message to AI chatbot
GET    /api/health/insights           # Get personalized health insights
```

#### 👤 **User Management**

```http
POST   /api/auth/signup               # Register new user
POST   /api/auth/login                # User login
POST   /api/auth/logout               # User logout
GET    /api/user/profile              # Get user profile
PUT    /api/user/profile              # Update user profile
PUT    /api/user/health-profile       # Update health questionnaire
GET    /api/user/preferences          # Get user preferences
PUT    /api/user/preferences          # Update preferences
```

#### 📊 **Data Management**

```http
GET    /api/user/scan-history         # Get scan history
GET    /api/user/favorites            # Get favorite products
POST   /api/user/favorites            # Add to favorites
DELETE /api/user/favorites/{id}       # Remove from favorites
GET    /api/user/statistics           # Get user statistics
```

#### 📝 **Content**

```http
GET    /api/blogs                     # Get blog articles
GET    /api/blogs/{id}                # Get specific article
GET    /api/blogs/categories          # Get blog categories
POST   /api/blogs                     # Create blog post (admin)
```

### 🔧 Integration Points in Code

The app has clearly marked integration points in service classes. Search for `TODO` comments to find where to add your API calls.

#### 1. **Authentication Service** 
Location: `lib/shared/services/auth_service.dart`

```dart
class AuthService {
  // TODO: Replace with your authentication API
  Future<User?> signInWithEmail(String email, String password) async {
    // Connect to your API endpoint: POST /api/auth/login
  }
  
  Future<User?> signUpWithEmail(String email, String password) async {
    // Connect to your API endpoint: POST /api/auth/signup
  }
  
  Future<void> signOut() async {
    // Connect to your API endpoint: POST /api/auth/logout
  }
}
```

#### 2. **Food Analysis Service**
Location: `lib/shared/services/food_service.dart`

```dart
class FoodService {
  // TODO: Connect to your Agentic AI backend
  Future<FoodAnalysis> analyzeBarcode(String barcode) async {
    // Connect to: POST /api/scan/barcode
  }
  
  Future<FoodAnalysis> analyzeImage(File image) async {
    // Connect to: POST /api/scan/photo
  }
  
  Future<List<Alternative>> getAlternatives(String foodId) async {
    // Connect to: GET /api/food/{id}/alternatives
  }
}
```

#### 3. **User Profile Service**
Location: `lib/shared/services/user_service.dart`

```dart
class UserService {
  // TODO: Connect to your user management API
  Future<UserProfile> getProfile() async {
    // Connect to: GET /api/user/profile
  }
  
  Future<void> updateHealthProfile(HealthProfile profile) async {
    // Connect to: PUT /api/user/health-profile
  }
  
  Future<List<ScanHistory>> getHistory() async {
    // Connect to: GET /api/user/scan-history
  }
}
```

### 📊 Data Models & API Responses

The app expects specific JSON structures from the backend. All models are defined in `lib/shared/models/`.

#### Example: Food Analysis Response

```json
{
  "id": "analysis_123",
  "name": "Organic Whole Milk",
  "brand": "Organic Valley",
  "healthScore": 7.5,
  "nutritionFacts": {
    "calories": 150,
    "protein": 8,
    "carbs": 12,
    "fat": 8,
    "fiber": 0,
    "sugar": 12,
    "sodium": 125
  },
  "ingredients": ["Organic Grade A Milk", "Vitamin D3"],
  "aiInsights": {
    "safetyScore": 85,
    "personalizedWarnings": [
      {
        "type": "allergen",
        "message": "Contains lactose",
        "severity": "medium"
      }
    ],
    "recommendations": "Consume in moderation",
    "alternatives": [...]
  }
}
```

### 🚀 Quick Integration Steps

1. **Set up your backend** with the required endpoints
2. **Update the API base URL** in service files (search for `_baseUrl`)
3. **Add authentication tokens** to API headers
4. **Test each endpoint** individually
5. **Switch from mock to production mode** by updating `kDevelopmentMode` flag
6. **Handle errors** and edge cases
7. **Test the complete flow** end-to-end

### 📚 Detailed Documentation

For comprehensive backend integration requirements, including:
- Detailed API specifications
- Request/response examples
- Agentic AI integration requirements
- Performance requirements
- Security guidelines

See: **[BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)**

---

## 📸 App Screenshots & Demo

> **Coming Soon**: Screenshots and demo videos will be added here showcasing:
> - Welcome & onboarding flow
> - Authentication screens
> - Home dashboard with health insights
> - Barcode and photo scanning interface
> - Detailed food analysis results
> - AI chatbot conversations
> - Profile and settings management
> - Scan history and favorites

---

## 🧪 Testing the App

### Current Functionality (Development Mode)

The app is fully functional with mock data, allowing you to experience all features without backend integration:

#### ✅ **Fully Working Features**

1. **🎬 Welcome Flow**
   - Beautiful animated onboarding
   - Feature showcase with smooth transitions
   - Swipe navigation between screens

2. **🔐 Authentication**
   - Complete signup flow with validation
   - Login with email/password
   - Health questionnaire integration
   - Mock social login buttons (UI only)
   - All forms with real-time validation

3. **🏠 Home Dashboard**
   - Personalized greetings
   - Health score display
   - Quick action buttons
   - Recent scans preview
   - Nutrition tips carousel

4. **📊 Scan Interface**
   - Dual-mode scanner UI
   - Barcode scanner screen (camera integration pending)
   - Photo capture screen (camera integration pending)
   - Manual product entry
   - Scanner tutorial and tips

5. **🔍 Food Analysis**
   - Comprehensive analysis screen with mock data
   - Health score visualization
   - Detailed nutritional breakdown
   - Ingredient analysis
   - Alternative product suggestions
   - Allergen warnings
   - Pros and cons display

6. **💬 AI Chatbot**
   - Interactive chat interface
   - Message sending and receiving (mock responses)
   - Context-aware conversation UI
   - Quick suggestion chips
   - Chat history

7. **📝 Profile Management**
   - User profile display
   - Health goal tracking
   - Settings customization
   - Theme switching (dark/light)
   - Preferences management

8. **📚 History & Favorites**
   - Scan history with filtering
   - Statistics and trends
   - Favorites management
   - Search functionality

9. **📰 Blog Section**
   - Article listings
   - Category filtering
   - Article reading interface
   - Blog creation UI (for future content management)

### 🧪 Testing Guide

Follow these steps to test the app comprehensively:

#### Step 1: Initial Launch
```bash
# Start the app
flutter run

# Expected: Welcome/onboarding screen appears
```

#### Step 2: Authentication Flow
1. Complete the onboarding (swipe through screens)
2. Navigate to signup
3. Fill in the signup form (use any email format)
4. Complete the health questionnaire
5. Try login with the mock credentials:
   - Email: `test@foodlens.ai`
   - Password: `password123`

#### Step 3: Explore Home Dashboard
1. View personalized health summary
2. Check quick action buttons
3. Scroll through nutrition tips
4. Tap on recent scans (if any)

#### Step 4: Test Scanning Flow
1. Tap the scan button
2. Choose between barcode or photo mode
3. View the scanner interface
4. Try manual product entry
5. View analysis results with mock data

#### Step 5: Interact with Chatbot
1. Navigate to chatbot screen
2. Send sample questions
3. View mock AI responses
4. Test quick suggestion chips

#### Step 6: Profile & Settings
1. Open profile screen
2. View health statistics
3. Toggle between light/dark theme
4. Update preferences
5. View scan history

#### Step 7: Test Navigation
1. Use bottom navigation bar
2. Test back button navigation
3. Verify smooth transitions
4. Check responsive design on different screen sizes

### 🎯 Testing on Different Devices

```bash
# Test on Android phone
flutter run -d android

# Test on iOS simulator (macOS only)
flutter run -d iphone

# Test on Android emulator
flutter emulators
flutter emulators --launch <emulator-name>
flutter run

# Test on Chrome (web - limited features)
flutter run -d chrome
```

### 🐛 What to Look For

- ✅ Smooth animations and transitions
- ✅ Responsive layout on different screen sizes
- ✅ Theme switching works correctly
- ✅ Form validations provide helpful feedback
- ✅ Navigation flows logically
- ✅ Mock data displays correctly
- ✅ No crashes or errors in console
- ✅ Performance is smooth (60 FPS)

## 🔧 **Development Commands**

```bash
# Hot reload during development
r

# Hot restart
R

# Quit
q

# Debug inspector
w

# Performance overlay
p

# Repaint rainbow
a

# Platform overrides
o
```

## 📱 **Building for Release**

### Android APK
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS
```bash
flutter build ios --release
# Open ios/Runner.xcworkspace in Xcode for signing
```

## 🎯 Next Steps & Roadmap

### 🔌 For Backend Developers

If you're building the backend for FoodLens AI:

1. **Review Integration Requirements**
   - Read [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) for complete API specifications
   - Understand the Agentic AI requirements
   - Review expected data models and response formats

2. **Set Up Core Services**
   - Implement authentication endpoints
   - Create user management system
   - Set up database schema

3. **Integrate AI Services**
   - Connect food recognition AI/ML models
   - Implement OCR for nutrition label scanning
   - Set up barcode lookup system
   - Create personalized recommendation engine

4. **Test Integration**
   - Use the Flutter app as a client
   - Validate API responses match expected formats
   - Test error handling and edge cases
   - Ensure performance requirements are met

### 🚀 For Frontend Developers

If you're enhancing the Flutter app:

1. **Complete Camera Integration**
   - Implement barcode scanner using `mobile_scanner`
   - Add photo capture functionality using `camera`
   - Integrate image processing pipeline
   - Test on multiple devices

2. **Connect to Backend**
   - Update service classes with production API URLs
   - Implement proper authentication flow
   - Add error handling and retry logic
   - Implement offline caching

3. **Enhanced Features**
   - 🔔 Push notifications for health insights
   - 💾 Offline mode with local database
   - 📊 Advanced analytics and charts
   - 🔄 Sync across devices
   - 🌍 Multi-language support
   - ♿ Enhanced accessibility features

4. **Testing & Quality**
   - Write unit tests for business logic
   - Add widget tests for UI components
   - Create integration tests for user flows
   - Set up CI/CD pipeline
   - Perform performance profiling

### 📱 Deployment Checklist

When ready for production:

- [ ] Connect to production backend API
- [ ] Configure Firebase for production
- [ ] Add proper error tracking (Sentry, Firebase Crashlytics)
- [ ] Set up analytics (Firebase Analytics, Mixpanel)
- [ ] Add app performance monitoring
- [ ] Create app store assets (screenshots, descriptions)
- [ ] Prepare privacy policy and terms of service
- [ ] Test on multiple devices and OS versions
- [ ] Perform security audit
- [ ] Submit to App Store and Google Play

## 🐛 **Troubleshooting**

### VS Code Crashes (CRITICAL)

#### **GitHub Copilot Crashes (4GB RAM Systems)**
```bash
# SOLUTION 1: Use Copilot-safe ultra minimal configuration
# In VS Code: Run > Start Debugging > "Flutter (Copilot Safe - Ultra Minimal)"

# SOLUTION 2: Use Copilot-safe task
# Ctrl+Shift+P → "Tasks: Run Task" → "Flutter: Run (Copilot Safe - Ultra Minimal)"

# SOLUTION 3: Manual ultra-low memory limits for Copilot
export DART_VM_OPTIONS="--old_gen_heap_size=256 --new_gen_heap_size=64"
flutter run --no-sound-null-safety --enable-software-rendering
```

#### **"This window is not responding" Error**
```bash
# SOLUTION 1: Use workspace file
# Open FoodLens-AI.code-workspace instead of folder

# SOLUTION 2: Use crash prevention launch config
# In VS Code: Run > Start Debugging > "Flutter (Crash Prevention)"

# SOLUTION 3: Manual memory limits
export DART_VM_OPTIONS="--old_gen_heap_size=256"
flutter run --no-sound-null-safety
```

#### **VS Code Freezing During Copilot Usage**
1. Close all VS Code windows
2. Restart VS Code 
3. Open `FoodLens-AI.code-workspace` file
4. Use "Flutter (Copilot Safe - Ultra Minimal)" configuration
5. Copilot suggestions are automatically limited to Dart files only
6. Memory monitoring widget shows live usage in debug mode
2. Restart VS Code 
3. Open `FoodLens-AI.code-workspace` file
4. Use minimal resource settings (already configured)

**📖 Complete guide:** [VS_CODE_CRASH_PREVENTION.md](VS_CODE_CRASH_PREVENTION.md)

---

### Common Issues

#### 1. **Dependency Conflicts**
```bash
flutter clean
flutter pub get
```

#### 2. **Build Errors**
```bash
flutter doctor
flutter doctor --android-licenses
```

#### 3. **iOS Pod Issues**
```bash
cd ios
rm Podfile.lock
pod deintegrate
pod install
cd ..
```

#### 4. **Hot Reload Not Working**
```bash
# Full restart
flutter run --hot

# Clear cache
flutter clean
flutter pub get
flutter run
```

## 🤝 Contributing

We welcome contributions to FoodLens AI! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following the code style guidelines
4. **Test thoroughly** to ensure nothing breaks
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to your branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request** with a clear description of changes

### Development Guidelines

- Follow Flutter and Dart best practices
- Maintain consistent code formatting (use `dart format`)
- Add comments for complex logic
- Update documentation for new features
- Test on both Android and iOS when possible
- Keep dependencies up to date

### Areas for Contribution

- 🐛 Bug fixes and issue resolution
- ✨ New features and enhancements
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Test coverage improvements
- 🌍 Internationalization and localization
- ♿ Accessibility improvements

---

## 📞 Support & Resources

### Documentation

- 📘 **[Flutter Documentation](https://docs.flutter.dev)** - Official Flutter docs
- 📗 **[Dart Documentation](https://dart.dev/guides)** - Dart language guide
- 📙 **[Riverpod Guide](https://riverpod.dev)** - State management
- 📕 **[GoRouter Documentation](https://pub.dev/packages/go_router)** - Navigation
- 📔 **[Material 3 Guidelines](https://m3.material.io)** - Design system
- 📖 **[Backend Integration](BACKEND_INTEGRATION.md)** - API specifications

### Community & Help

- 💬 **Issues**: Report bugs or request features in [GitHub Issues](https://github.com/mohitkattungal/FoodLens-AI---Flutter-App/issues)
- 🔧 **Discussions**: Join discussions in [GitHub Discussions](https://github.com/mohitkattungal/FoodLens-AI---Flutter-App/discussions)
- 📧 **Contact**: Reach out to the maintainers

### Useful Resources

- [Flutter Cookbook](https://docs.flutter.dev/cookbook)
- [Pub.dev Packages](https://pub.dev)
- [Flutter Community](https://flutter.dev/community)
- [Stack Overflow - Flutter](https://stackoverflow.com/questions/tagged/flutter)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Flutter Team** for the amazing framework
- **Firebase** for backend services
- **Material Design** for design guidelines
- **Open Source Community** for incredible packages and tools

---

## 🌟 Star History

If you find FoodLens AI helpful, please consider giving it a star ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ by the FoodLens AI Team**

[Report Bug](https://github.com/mohitkattungal/FoodLens-AI---Flutter-App/issues) • [Request Feature](https://github.com/mohitkattungal/FoodLens-AI---Flutter-App/issues) • [Documentation](BACKEND_INTEGRATION.md)

</div>
=======
# FoodLens AI

A comprehensive AI-powered food analysis application using LangChain and LangGraph for agentic workflows. This project provides food product analysis through OCR text extraction, barcode scanning, and AI-based health assessment.

## Features

- **Product Identification**: Analyze food products using OCR text and barcode scanning
- **Product Categorization**: Classify food products into categories using Gemini AI
- **Health Assessment**: Calculate health scores based on nutritional information
- **Alternative Recommendation**: Suggest healthier alternative products
- **Claim Verification**: Verify health claims on product packaging (Premium feature)
- **FSSAI Compliance Check**: Verify regulatory compliance (Premium feature)
- **LangGraph Workflow**: Orchestrated workflow using LangGraph for agentic AI

## Architecture

The application uses a modular architecture with the following components:

1. **FastAPI Backend**: Provides RESTful API endpoints
2. **LangChain Tools**: Wraps core functionality in LangChain-compatible tools
3. **LangGraph Workflow**: Orchestrates the analysis workflow using a state-based graph
4. **OCR Processing**: Extracts text from product images
5. **Barcode Scanning**: Retrieves product information from barcodes
6. **Gemini AI Integration**: Powers product categorization and analysis

## Project Structure

```
FoodLens/
│
├── langchain_agents/        # LangChain and LangGraph components
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # LangChain agent definition
│   ├── graph.py             # LangGraph workflow definition
│   └── tools.py             # LangChain tools implementation
│
├── main.py                  # FastAPI application
├── search_utils.py          # Core search functionality
├── demo.py                  # Demo script for testing
└── requirements.txt         # Project dependencies
```

## Installation

1. Clone the repository
2. Set up a Python virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
# Set your Google API key for Gemini AI
export GOOGLE_API_KEY="your-api-key-here"
```

## Usage

### Running the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### API Endpoints

- **POST /api/v1/analyze_food**: Analyze food product with OCR text and/or barcode data
- **POST /api/v1/analyze_image**: Analyze food product from an uploaded image
- **GET /api/v1/health**: Health check endpoint

### Running the Demo

```bash
python demo.py
```

This will run a sample analysis using predefined OCR text.

## LangGraph Workflow

The application uses LangGraph to orchestrate the analysis workflow:

1. **Extract Product Info**: Process OCR text and barcode data
2. **Categorize Product**: Determine product category and type
3. **Calculate Health Score**: Analyze nutritional data and calculate health score
4. **Find Alternatives**: Search for healthier alternative products
5. **Verify Claims and Compliance**: Check health claims and regulatory compliance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
>>>>>>> 3f36d76d522e9cc38f214b8eb55fe5ba1db4b7d3
