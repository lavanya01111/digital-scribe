# training/personalize.py
# Fine-tunes the model on samples from a specific student.
# Called when a student has 50+ labeled samples in the DB.

# 1. Download student samples from Supabase Storage
# 2. Create a small Dataset from those samples
# 3. Fine-tune for just 2-3 epochs (avoid overfitting)
# 4. Save as models_saved/student_{student_id}/
# 5. Load this student-specific model during their exam

# This pattern is called "few-shot fine-tuning" and
# can reduce WER by 20-40% for individual students.
