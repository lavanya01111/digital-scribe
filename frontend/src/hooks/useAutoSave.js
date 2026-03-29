// src/hooks/useAutoSave.js
// Automatically saves student answer to Supabase every 5 seconds.
// Prevents data loss if browser crashes or exam time runs out.

import { useEffect, useRef } from "react";
import { supabase } from "../lib/supabase";

export function useAutoSave({ answerId, text, examId, studentId }) {
  const timerRef = useRef(null);

  useEffect(() => {
    // Clear any existing timer before setting a new one
    clearInterval(timerRef.current);

    timerRef.current = setInterval(async () => {
      if (!text) return; // Nothing to save
      await supabase.from("answers").upsert({
        id: answerId,
        exam_id: examId,
        student_id: studentId,
        corrected_text: text,
        saved_at: new Date().toISOString(),
      });
    }, 5000); // Every 5 seconds

    // Cleanup on unmount
    return () => clearInterval(timerRef.current);
  }, [text]);
}
