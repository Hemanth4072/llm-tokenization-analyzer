export interface LanguageSample {
  code: string;
  label: string;
  text: string;
}

export const LANGUAGE_SAMPLES: LanguageSample[] = [
  { code: "en", label: "English", text: "Large language models process text as tokens, not characters." },
  { code: "hi", label: "Hindi", text: "बड़े भाषा मॉडल पाठ को टोकन के रूप में संसाधित करते हैं।" },
  { code: "te", label: "Telugu", text: "పెద్ద భాషా నమూనాలు వచనాన్ని టోకెన్లుగా ప్రాసెస్ చేస్తాయి." },
  { code: "ta", label: "Tamil", text: "பெரிய மொழி மாதிரிகள் உரையை டோக்கன்களாக செயலாக்குகின்றன." },
  { code: "ja", label: "Japanese", text: "大規模言語モデルはテキストを文字ではなくトークンとして処理します。" },
  { code: "ar", label: "Arabic", text: "تعالج نماذج اللغة الكبيرة النصوص كرموز وليس كأحرف." },
];
