import { useState, useEffect, useCallback } from "react";
import { supabase } from "@/integrations/supabase/client";

/* ── Types ── */
interface Question {
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
  difficulty: "easy" | "medium" | "hard";
}

interface QuizData {
  quiz_date: string;
  day_theme: string;
  questions: Question[];
}

/* ── Day themes ── */
const DAY_THEMES: Record<number, string> = {
  1: "Bollywood & Indian Cinema",
  2: "Technology & Startups",
  3: "Geography & Travel",
  4: "Indian History & Culture",
  5: "Food & Regional Cuisines",
  6: "Sports & Indian Athletes",
  0: "Mixed Weekly Review",
};

const DAY_NAMES: Record<number, string> = {
  1: "🎬 Movie Monday",
  2: "💻 Tech Tuesday",
  3: "🌍 Wanderlust Wednesday",
  4: "⏪ Throwback Thursday",
  5: "🍛 Foodie Friday",
  6: "🏏 Sports Saturday",
  0: "🐙 Surprise Sunday",
};

/* ── localStorage helpers ── */
function getTodayKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function getCompletedQuiz(): { date: string; score: number; answers: number[] } | null {
  try {
    const raw = localStorage.getItem("daily7_completed");
    if (!raw) return null;
    const data = JSON.parse(raw);
    return data.date === getTodayKey() ? data : null;
  } catch {
    return null;
  }
}

function saveCompletedQuiz(score: number, answers: number[]) {
  localStorage.setItem(
    "daily7_completed",
    JSON.stringify({ date: getTodayKey(), score, answers })
  );
  updateStreak(score);
  // Record completion server-side for engagement tracking
  supabase.rpc("record_quiz_completion", { p_quiz_date: getTodayKey() }).then();
}

function getStreak(): number {
  try {
    return parseInt(localStorage.getItem("daily7_streak") || "0", 10);
  } catch {
    return 0;
  }
}

function updateStreak(score: number) {
  try {
    const streakData = JSON.parse(localStorage.getItem("daily7_streak_data") || "{}");
    const today = getTodayKey();
    const yd = new Date(Date.now() - 86400000);
    const yesterday = `${yd.getFullYear()}-${String(yd.getMonth() + 1).padStart(2, "0")}-${String(yd.getDate()).padStart(2, "0")}`;

    if (score >= 4) {
      if (streakData.lastDate === yesterday || streakData.lastDate === today) {
        streakData.count = (streakData.count || 0) + (streakData.lastDate === today ? 0 : 1);
      } else {
        streakData.count = 1;
      }
      streakData.lastDate = today;
    } else {
      streakData.count = 0;
      streakData.lastDate = today;
    }

    localStorage.setItem("daily7_streak_data", JSON.stringify(streakData));
    localStorage.setItem("daily7_streak", String(streakData.count));
  } catch {}
}

function getScoreEmoji(score: number): string {
  if (score === 7) return "🏆";
  if (score >= 5) return "🌟";
  if (score >= 3) return "👍";
  return "📚";
}

function getScoreMessage(score: number): string {
  if (score === 7) return "Perfect score!";
  if (score >= 5) return "Great job!";
  if (score >= 3) return "Not bad!";
  return "Keep learning!";
}

/* ── Component ── */
export default function DailyQuiz() {
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [state, setState] = useState<"preview" | "playing" | "result">("preview");
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [showExplanation, setShowExplanation] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showAnswers, setShowAnswers] = useState(false);

  // Load quiz data
  useEffect(() => {
    (async () => {
      const today = getTodayKey();
      const { data } = await (supabase as any)
        .from("daily_quiz")
        .select("quiz_date, day_theme, questions")
        .eq("quiz_date", today)
        .single();

      if (data) {
        setQuiz(data as QuizData);
        const completed = getCompletedQuiz();
        if (completed) {
          setScore(completed.score);
          setAnswers(completed.answers);
          setState("result");
        }
      }

      setStreak(getStreak());
    })();
  }, []);

  const handleAnswer = useCallback(
    (idx: number) => {
      if (selected !== null || !quiz) return;
      setSelected(idx);
      setShowExplanation(true);

      const isCorrect = idx === quiz.questions[currentQ].correct_index;
      const newAnswers = [...answers, idx];
      const newScore = score + (isCorrect ? 1 : 0);
      setAnswers(newAnswers);
      if (isCorrect) setScore(newScore);

      setTimeout(() => {
        if (currentQ + 1 >= quiz.questions.length) {
          saveCompletedQuiz(newScore, newAnswers);
          setStreak(getStreak());
          setState("result");
        } else {
          setCurrentQ((q) => q + 1);
          setSelected(null);
          setShowExplanation(false);
        }
      }, 2000);
    },
    [selected, quiz, currentQ, answers, score]
  );

  const handleShare = useCallback(() => {
    if (!quiz) return;
    const text = `I scored ${score}/7 on today's Daily 7 Quiz on The Videshi! ${getScoreEmoji(score)} ${quiz.day_theme} | thevideshi.com`;
    if (navigator.share) {
      navigator.share({ text }).catch(() => {});
    } else {
      navigator.clipboard.writeText(text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  }, [quiz, score]);

  if (!quiz) return null;

  /* ── Preview state ── */
  if (state === "preview") {
    const dayName = DAY_NAMES[new Date().getDay()] || quiz.day_theme;
    return (
      <section className="mb-14">
        <div className="container">
          <div
            className="rounded-xl overflow-hidden"
            style={{ border: "1px solid #E5E5E5" }}
          >
            <div
              className="px-5 py-3 flex items-center justify-between"
              style={{ background: "#0B1D3A" }}
            >
              <div>
                <h3 className="text-white font-serif font-bold text-lg">
                  Daily 7
                </h3>
                <p className="text-white/60 text-xs mt-0.5">{dayName}</p>
              </div>
              <div className="flex items-center gap-3">
                {streak > 0 && (
                  <span className="text-amber-400 text-xs font-semibold">
                    🔥 {streak} day streak
                  </span>
                )}
                <span className="bg-white/15 text-white text-[11px] font-semibold px-2.5 py-1 rounded-full">
                  7 Questions
                </span>
              </div>
            </div>
            <div className="px-5 py-3 text-center">
              <p className="text-sm text-muted-foreground mb-3">
                Test your knowledge with today's quiz
              </p>
              <button
                onClick={() => setState("playing")}
                className="px-6 py-2 rounded-lg text-sm font-semibold text-white transition-colors"
                style={{ background: "#A32D2D" }}
              >
                Start Quiz →
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  /* ── Playing state ── */
  if (state === "playing") {
    const q = quiz.questions[currentQ];
    const isCorrect = selected !== null && selected === q.correct_index;
    const dayName = DAY_NAMES[new Date().getDay()] || quiz.day_theme;

    return (
      <section className="mb-14">
        <div className="container">
          <div
            className="rounded-xl overflow-hidden"
            style={{ border: "1px solid #E5E5E5" }}
          >
            {/* Header */}
            <div
              className="px-5 py-2.5 flex items-center justify-between"
              style={{ background: "#0B1D3A" }}
            >
              <span className="text-white/80 text-xs font-semibold">
                {dayName}
              </span>
              <div className="flex items-center gap-2">
                {quiz.questions.map((_, i) => (
                  <span
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{
                      background:
                        i < currentQ
                          ? answers[i] === quiz.questions[i].correct_index
                            ? "#4ade80"
                            : "#f87171"
                          : i === currentQ
                          ? "#fff"
                          : "rgba(255,255,255,0.25)",
                    }}
                  />
                ))}
              </div>
              <span className="text-white text-xs tabular-nums">
                {currentQ + 1}/7
              </span>
            </div>

            {/* Question */}
            <div className="px-5 py-3">
              <div className="flex items-start gap-2 mb-1">
                <span
                  className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded"
                  style={{
                    background:
                      q.difficulty === "hard"
                        ? "#fef2f2"
                        : q.difficulty === "medium"
                        ? "#fffbeb"
                        : "#f0fdf4",
                    color:
                      q.difficulty === "hard"
                        ? "#991b1b"
                        : q.difficulty === "medium"
                        ? "#92400e"
                        : "#166534",
                  }}
                >
                  {q.difficulty}
                </span>
              </div>
              <p className="font-serif font-bold text-base md:text-lg leading-snug mb-3">
                {q.question}
              </p>

              <div className="grid gap-1.5">
                {q.options.map((opt, i) => {
                  let bg = "bg-white";
                  let border = "border-neutral-200";
                  let text = "text-foreground";

                  if (selected !== null) {
                    if (i === q.correct_index) {
                      bg = "bg-green-50";
                      border = "border-green-400";
                      text = "text-green-900";
                    } else if (i === selected && !isCorrect) {
                      bg = "bg-red-50";
                      border = "border-red-400";
                      text = "text-red-900";
                    } else {
                      bg = "bg-neutral-50";
                      border = "border-neutral-100";
                      text = "text-muted-foreground";
                    }
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => handleAnswer(i)}
                      disabled={selected !== null}
                      className={`w-full text-left px-3 py-2 rounded-lg border text-sm transition-all ${bg} ${border} ${text} ${
                        selected === null
                          ? "hover:border-neutral-400 hover:shadow-sm cursor-pointer active:scale-[0.99]"
                          : "cursor-default"
                      }`}
                    >
                      <span className="font-medium mr-2 text-muted-foreground">
                        {String.fromCharCode(65 + i)}.
                      </span>
                      {opt}
                    </button>
                  );
                })}
              </div>

              {/* Explanation */}
              {showExplanation && (
                <div
                  className="mt-2 px-3 py-2 rounded-lg text-sm"
                  style={{
                    background: isCorrect ? "#f0fdf4" : "#fef2f2",
                    borderLeft: `3px solid ${isCorrect ? "#4ade80" : "#f87171"}`,
                  }}
                >
                  <span className="font-semibold">
                    {isCorrect ? "✓ Correct!" : "✗ Incorrect."}
                  </span>{" "}
                  {q.explanation}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>
    );
  }

  /* ── Result state ── */
  const dayName = DAY_NAMES[new Date().getDay()] || quiz.day_theme;
  return (
    <section className="mb-14">
      <div className="container">
        <div
          className="rounded-xl overflow-hidden"
          style={{ border: "1px solid #E5E5E5" }}
        >
          <div
            className="px-5 py-3 text-center"
            style={{ background: "#0B1D3A" }}
          >
            <span className="text-3xl block mb-1">{getScoreEmoji(score)}</span>
            <h3 className="text-white font-serif font-bold text-xl">
              {score}/7
            </h3>
            <p className="text-white/60 text-sm">{getScoreMessage(score)}</p>
          </div>
          <div className="px-5 py-4">
            <div className="flex items-center justify-center gap-4 mb-3">
              {streak > 0 && (
                <span className="text-sm font-semibold text-amber-600">
                  🔥 {streak} day streak
                </span>
              )}
              <span className="text-sm text-muted-foreground">
                {dayName}
              </span>
            </div>

            {/* Collapsed: toggle to show answers */}
            <button
              onClick={() => setShowAnswers((v) => !v)}
              className="w-full flex items-center justify-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors py-1 mb-3"
            >
              {showAnswers ? "Hide Questions" : "See Questions & Answers"}
              <svg
                className={`w-3.5 h-3.5 transition-transform ${showAnswers ? "rotate-180" : ""}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Answer summary — collapsible */}
            {showAnswers && (
              <div className="grid gap-1 mb-4">
                {quiz.questions.map((q, i) => {
                  const userAnswer = answers[i];
                  const correct = userAnswer === q.correct_index;
                  return (
                    <div
                      key={i}
                      className="flex items-start gap-2 text-sm py-1"
                    >
                      <span className="mt-0.5 shrink-0">
                        {correct ? "✅" : "❌"}
                      </span>
                      <div className="min-w-0">
                        <p className="font-medium leading-snug">{q.question}</p>
                        {!correct && (
                          <p className="text-xs text-muted-foreground mt-0.5">
                            Answer: {q.options[q.correct_index]}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            <div className="flex items-center justify-center gap-3">
              <button
                onClick={handleShare}
                className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-colors"
                style={{ background: "#A32D2D" }}
              >
                {copied ? "Copied! ✓" : "Share Score"}
              </button>
            </div>
            <p className="text-center text-xs text-muted-foreground mt-2">
              Come back tomorrow for a new quiz!
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
