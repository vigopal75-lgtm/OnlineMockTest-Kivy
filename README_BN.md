# Online Mock Test — Python + Kivy

## Project
This is a native Android app implementation of the uploaded Online Mock Test HTML interface.

### Included
- MCQ exam interface, option selection, Previous/Next, Save & Next
- Clear Response, Mark Review, Question Palette and status colors
- 90-minute timer, submit confirmation and negative marking (0.33)
- Result calculation and answer review
- A/B/C/D, arrow and Enter keyboard shortcuts where a physical keyboard is available
- Bengali question text stored separately in `questions/questions.json`

## Build APK using Google Colab
1. Download and extract `OnlineMockTest_Kivy.zip` on your computer if desired.
2. Open https://colab.research.google.com/
3. Create a new notebook.
4. Upload `OnlineMockTest_Kivy.zip` when prompted by the first cell in `Google_Colab_APK_Guide.py`.
5. Run the notebook cells from top to bottom.
6. The final cell downloads the APK. Install it on an Android phone (allow installation from that source if Android asks).

The first Android build downloads SDK/NDK components and can take 20–60 minutes. Keep the Colab session active.

## Build locally (Linux/WSL)
Install Buildozer and Android build dependencies, then run:
```bash
buildozer -v android debug
```
APK output: `bin/`

## Change questions
Edit `questions/questions.json`. Each item:
```json
{
  "q": "প্রশ্ন",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": 0
}
```
`answer` is zero-based: 0=A, 1=B, 2=C, 3=D.

## Important source-data note
The uploaded HTML contains 72 question records in its JavaScript array, although its start screen hard-codes “100” as the displayed total. The source repeats the same eight-question group many times. This project imports those records as found and does not silently remove duplicates or correct answer keys. Please review the imported questions and answer indices before using this as a real exam.


## GitHub Actions দিয়ে APK তৈরি

1. এই প্রজেক্টের সব ফাইল GitHub repository-র `main` branch-এ upload করুন।
2. Repository-তে `.github/workflows/android-apk.yml` ফাইলটি থাকতে হবে।
3. GitHub-এ repository খুলে **Actions** tab-এ যান।
4. **Build Android APK** workflow নির্বাচন করে **Run workflow** চাপুন। `main` branch-এ push করলেও build শুরু হবে।
5. Build সফল হলে workflow run-এর নিচে **Artifacts** থেকে `OnlineMockTest-APK` ZIP ডাউনলোড করুন।
6. ZIP extract করলে `.apk` ফাইল পাবেন; সেটি Android ফোনে কপি করে install করুন।

প্রথম build-এ Android SDK/NDK ডাউনলোডের কারণে সময় লাগতে পারে। Build ব্যর্থ হলে Actions-এর failed step-এর log দেখে সমস্যা শনাক্ত করতে হবে। APK এই workflow-তে GitHub Artifact হিসেবে সংরক্ষিত হয়; এটি নিজে থেকে Play Store-এ প্রকাশ করে না।
