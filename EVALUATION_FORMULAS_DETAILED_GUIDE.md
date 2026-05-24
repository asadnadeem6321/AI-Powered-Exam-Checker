# AI-Powered Exam Checker: Complete Evaluation Formulas & Scoring Logic
## Detailed Technical Guide for Supervisors & Stakeholders

---

## Table of Contents
1. [System Overview & Architecture](#system-overview--architecture)
2. [Complete Scoring Pipeline](#complete-scoring-pipeline)
3. [Detailed Formula Explanations](#detailed-formula-explanations)
4. [Subpoints Extraction & Matching](#subpoints-extraction--matching)
5. [Real-World Examples](#real-world-examples)
6. [Quality Assurance & Penalties](#quality-assurance--penalties)

---

## System Overview & Architecture

### How the System Works (High Level)

When a student submits an answer to a question, the system evaluates it through a **hybrid pipeline** that combines:

1. **Neural Component (SBERT)**: Uses pre-trained AI model to compute semantic similarity
2. **Deterministic Component (Context Scorer)**: Uses rule-based logic to extract detailed metrics
3. **Consistency Check (NLI)**: Uses Natural Language Inference to detect logical contradictions
4. **Final Scoring**: Combines all components with specific weights

```
Student Answer Input
         ↓
    ┌────┴────┐
    ├ SBERT Similarity (0-100%)
    ├ Keyword Coverage
    ├ Length Adequacy
    ├ Structure Quality
    ├ Completeness (Subpoints)
    ├ Clarity Score
    └ NLI Contradiction Check
         ↓
    Contextual Composite Score (0-100%)
         ↓
    Hybrid Final Score = 70% Semantic + 30% Context
         ↓
    Penalties & Caps Applied
         ↓
    Final Score % → Converted to Marks
         ↓
Grade Assignment (A, B, C, D, E, F)
```

---

## Complete Scoring Pipeline

### Pipeline Inputs & Outputs

**INPUTS:**
- `student_answer`: Text of student's response
- `model_answer`: Text of expected/correct answer (pre-loaded from question database)
- `question_text`: The question itself
- `marks`: Total marks allocated to this question

**PROCESSING STEPS:**

1. **Text Cleaning & Normalization**
   - Remove extra whitespace, standardize formatting
   - Convert to lowercase for comparison
   - Remove timestamps/metadata

2. **Component Scoring** (6 independent metrics)
   - Keyword Coverage Score (0-100%)
   - Length Adequacy Score (0-100%)
   - Structure Quality Score (0-100%)
   - Completeness Score (0-100%)
   - Clarity Score (0-100%)
   - Accuracy Score (0-100%)

3. **Contextual Composite Score**
   - Weighted combination of 6 metrics
   - Formula: `0.20K + 0.15L + 0.15S + 0.20C + 0.20A + 0.10Cl`
   - Result: 0-100%

4. **Semantic Similarity Score (SBERT)**
   - AI model compares semantic meaning
   - Result: 0-100%

5. **Hybrid Final Score (Before Penalties)**
   - Formula: `(0.7 × Similarity%) + (0.3 × Contextual%)`
   - Result: 0-100%

6. **NLI Contradiction Check**
   - Detects if student answer logically contradicts the correct answer
   - If contradiction ≥ 65% confidence: Cap score at 5%

7. **Penalty Adjustments**
   - Semantic Mismatch Penalty: Reduces score for topically related but wrong answers
   - Hard Relevance Caps: Prevents high scores when key components missing
   - Result: Final Score % (0-100%)

8. **Marks Calculation**
   - Formula: `obtained_marks = (final_score% / 100) × total_marks_for_question`

**OUTPUT FIELDS:**
```
{
  'similarity_score': float (0-100%),
  'contextual_score': float (0-100%),
  'final_score_pct': float (0-100%),
  'obtained_marks': float (points),
  'keyword_score': float,
  'length_score': float,
  'structure_score': float,
  'completeness_score': float,
  'clarity_score': float,
  'accuracy_score': float,
  'matched_keywords': list of strings,
  'matched_subpoints': list of strings,
  'total_subpoints': integer,
  'nli_contradiction': float (0-1 probability),
  'nli_entailment': float (0-1 probability),
  'confidence': string ('high' or 'low'),
  'strengths': list of strings,
  'weaknesses': list of strings,
  'feedback': string explanation
}
```

---

## Detailed Formula Explanations

### Component 1: Keyword Coverage Score (K)

**Purpose:** Measure how much of the key terminology from the expected answer appears in the student's answer.

**Algorithm:**

1. **Extract Keywords from Model Answer**
   - Tokenize the model answer into words
   - Remove "stopwords" (common words like "the", "a", "is", "and", etc.)
   - Keep only content words with 3+ characters
   - Apply lightweight stemming (remove common suffixes: -ing, -ed, -s)
   - Rank by frequency (most common first)
   - Take top 25 keywords

   **Example:**
   ```
   Model Answer: "Photosynthesis is the process where plants use sunlight, 
                   water, and carbon dioxide to produce glucose and oxygen"
   
   Raw tokens: [photosynthesis, process, plants, use, sunlight, water, 
                carbon, dioxide, produce, glucose, oxygen]
   
   Top Keywords (by frequency): 
   [photosynthesis, process, plants, sunlight, water, carbon, dioxide, oxygen, glucose]
   ```

2. **Tokenize Student Answer**
   - Apply same stopword removal and stemming
   - Extract unique content tokens

   **Example:**
   ```
   Student Answer: "Plants make energy from sunlight and water"
   
   Tokens: [plants, energy, sunlight, water]
   ```

3. **Calculate Keyword Overlap**
   - Count how many expected keywords appear in student tokens
   - Formula: `Keyword_Score = (Matched_Keywords / Total_Keywords) × 100`

   **Example:**
   ```
   Expected Keywords: 9 [photosynthesis, process, plants, sunlight, water, 
                         carbon, dioxide, oxygen, glucose]
   
   Student Tokens: 4 [plants, energy, sunlight, water]
   
   Matched: 3 [plants, sunlight, water]
   
   Keyword Score = (3 / 9) × 100 = 33.33%
   ```

**Output Fields:**
- `keyword_score`: 0-100%
- `matched_keywords`: ['plants', 'sunlight', 'water']
- `matched_count`: 3
- `total_keywords`: 9

**Why This Matters:** Ensures student actually knows the expected terminology, not just rambling about the topic.

---

### Component 2: Length Adequacy Score (L)

**Purpose:** Verify that the student answer is comprehensive enough (not too brief).

**Algorithm:**

1. **Count Words in Both Answers**
   - Use tokenized word count (after stemming)

   **Example:**
   ```
   Model Answer: "Photosynthesis is the process where plants use sunlight, 
                   water, and carbon dioxide to produce glucose and oxygen"
   Word Count: 22 words
   
   Student Answer: "Plants make energy from sunlight and water"
   Word Count: 8 words
   ```

2. **Calculate Length Ratio**
   - Formula: `Ratio = Student_Words / Model_Words = 8 / 22 = 0.364`

3. **Apply Floor & Ceiling**
   - Minimum acceptable ratio: 50% (too short = incomplete)
   - Maximum useful ratio: 100% (no extra credit for verbose)
   - Formula: `clamped_ratio = min(max(ratio, 0.5), 1.0)`
   - Example: `clamped_ratio = min(max(0.364, 0.5), 1.0) = 0.5`

4. **Convert to Score**
   - Formula: `Length_Score = clamped_ratio × 100`
   - Example: `Length_Score = 0.5 × 100 = 50.0%`

**Interpretation:**
- 100%: Answer length matches expected (50-100% of model)
- 75%: Answer is slightly brief but acceptable
- 50%: Answer is at minimum acceptable length
- <50%: Answer is too brief (will be scored at 50%)

**Output Fields:**
- `length_score`: 0-100%
- `student_word_count`: 8
- `model_word_count`: 22
- `length_ratio`: 0.364

**Why This Matters:** A one-sentence answer might be semantically correct but miss important details. Length ensures attempt at completeness.

---

### Component 3: Structure Quality Score (S)

**Purpose:** Evaluate the clarity and organization of how the answer is written.

**Algorithm:**

Uses 4 sub-metrics combined with weights:
- **30% Sentence Score**: How many complete sentences used?
- **25% Punctuation Score**: Does answer use proper punctuation?
- **25% Connective Score**: Are ideas linked logically (first, then, therefore, etc.)?
- **20% Bullet/Format Score**: Is answer formatted clearly?

**Sub-metric 1: Sentence Score (30%)**

```
Sentence Count → Normalized Score:
- 0 sentences: 0%
- 1 sentence: 33%
- 2 sentences: 67%
- 3+ sentences: 100%

Formula: sentence_score = min((sentence_count / 3.0), 1.0) × 100
```

**Example:**
```
Student Answer: "Plants use sunlight and water. They produce glucose and oxygen. 
                  This is called photosynthesis."
Sentence Count: 3
Sentence Score: min((3/3), 1.0) × 100 = 100%
```

**Sub-metric 2: Punctuation Score (25%)**

```
If answer contains any of: . ! ? ; ,
→ Score = 100%
Else
→ Score = 55%

Example: "Plants use sunlight water and oxygen"
No punctuation → Score = 55%

Example: "Plants use sunlight, water, and oxygen."
Has punctuation → Score = 100%
```

**Sub-metric 3: Connective Score (25%)**

Looks for logical connectives: first, second, then, next, finally, because, therefore, hence, thus, also, furthermore, moreover, however, in addition, for example, in summary

```
Count of connectives found
Formula: connective_score = min((count / 3.0), 1.0) × 100

Example:
Answer: "First, plants absorb water from soil. Second, they capture sunlight. 
         Finally, they produce glucose."
Connectives found: 3 (First, Second, Finally)
Connective Score: min((3/3), 1.0) × 100 = 100%
```

**Sub-metric 4: Bullet/Format Score (20%)**

```
If answer uses bulleted/numbered format:
→ Score = 100%
Else
→ Score = 60%

Example with bullets:
• Plants absorb water
• They capture sunlight
• They produce glucose
→ Score = 100%

Example without:
"Plants absorb water. They capture sunlight. They produce glucose."
→ Score = 60%
```

**Final Structure Score Calculation:**

```
Structure = (0.30 × sentence_score) + (0.25 × punctuation_score) 
          + (0.25 × connective_score) + (0.20 × bullet_score)

Example:
= (0.30 × 100) + (0.25 × 100) + (0.25 × 100) + (0.20 × 60)
= 30 + 25 + 25 + 12
= 92%
```

**Output Fields:**
- `structure_score`: 0-100%
- `sentence_count`: integer
- `punctuation_present`: boolean
- `connective_count`: integer
- `bullet_like`: boolean
- `readability_band`: 'poor'|'moderate'|'good'
- `avg_sentence_len`: float (words per sentence)

**Why This Matters:** Helps identify if student understands concepts well enough to explain clearly, not just list terms.

---

### Component 4: Completeness Score (C)

**Purpose:** Measure how many expected "subpoints" or concepts the student covered.

**Algorithm:**

**Step 1: Extract Expected Subpoints from Model Answer**

The system breaks the model answer into logical "subpoints" using these delimiters:
- Sentence boundaries (periods)
- Semicolons, colons
- Bullet points, dashes
- Logical connectors: "and", "also", "further", "moreover", "additionally"

**Example:**

```
Model Answer: "Photosynthesis is the process where plants convert light 
               energy into chemical energy. The process occurs in chloroplasts. 
               It requires water, carbon dioxide, and sunlight. The outputs 
               are glucose and oxygen."

Extracted Subpoints:
1. "photosynthesis process convert light energy chemical energy"
2. "process occurs chloroplasts"
3. "requires water carbon dioxide sunlight"
4. "outputs glucose oxygen"
```

Each subpoint is then tokenized (stopword removal, stemming).

**Step 2: Match Student Tokens to Subpoints**

For each subpoint, count how many of its tokens appear in the student answer.

```
Student Answer: "Plants make glucose from sunlight and water"
Student Tokens: {plants, make, glucose, sunlight, water}

Subpoint Match Algorithm:
For each subpoint:
  - Count matching tokens (token must be in student_tokens)
  - If matched tokens ≥ 60% of subpoint tokens → MATCHED
  
Subpoint 1: "photosynthesis process convert light energy chemical energy"
Tokens needed: 6, Needed to match: ceil(6 × 0.6) = 4
Tokens found: 0 → NOT MATCHED

Subpoint 3: "requires water carbon dioxide sunlight"
Tokens needed: 4, Needed to match: ceil(4 × 0.6) = 3
Tokens found: 2 (water, sunlight) → NOT MATCHED (need 3)

Subpoint 4: "outputs glucose oxygen"
Tokens needed: 2, Needed to match: ceil(2 × 0.6) = 2
Tokens found: 1 (glucose) → NOT MATCHED (need 2)

Total Matched: 0 / 4 = 25%
```

**Completeness Score Formula:**

```
Completeness = (matched_subpoints / total_subpoints) × 100

Example: (0 / 4) × 100 = 0%
```

**Output Fields:**
- `completeness_score`: 0-100%
- `matched_subpoints`: list of matched subpoint texts
- `total_subpoints`: total expected subpoints

**Why This Matters:** Ensures student covered all major aspects of the expected answer, not just partial understanding.

---

### Component 5: Clarity Score (Cl)

**Purpose:** Measure readability—is the answer easy to understand?

**Algorithm:**

Evaluates sentence length and writing quality:

**Base Clarity Score:**

```
Formula: clarity = 100 - min(60, 4 × |avg_sentence_len - 17|)

Where:
- avg_sentence_len = total_words / sentence_count
- Optimal sentence length: 17 words (research standard for clarity)
- Deviation penalizes both too-short and too-long sentences
```

**Example 1: Concise Answer**
```
Answer: "Plants absorb water. (3 words) They use sunlight. (3 words) 
         They produce glucose. (3 words)"

Sentence count: 3
Total words: 9
avg_sentence_len = 9 / 3 = 3 words

Deviation = |3 - 17| = 14
Penalty = 4 × 14 = 56 (capped at 60)
Base Clarity = 100 - 56 = 44%
```

**Example 2: Well-Balanced Answer**
```
Answer: "Photosynthesis is the biological process where plants use sunlight, 
         water, and carbon dioxide to synthesize glucose and release oxygen 
         as a byproduct."

Sentence count: 1
Total words: 27
avg_sentence_len = 27 / 1 = 27 words

Deviation = |27 - 17| = 10
Penalty = 4 × 10 = 40
Base Clarity = 100 - 40 = 60%
```

**Bonuses (+5% each, up to 4 bonuses):**
- Has 2+ sentences: +5%
- Has proper punctuation (. ! ? ; ,): +5%
- Has 12+ words: +5%

**Example Calculation with Bonuses:**
```
Base: 60%
+ Bonus (2+ sentences): +5%
+ Bonus (punctuation): +5%
+ Bonus (12+ words): +5%
Final Clarity = 60 + 15 = 75% (capped at 100%)
```

**Output Fields:**
- `clarity_score`: 0-100%
- `avg_sentence_len`: float

**Why This Matters:** Checks if student can express understanding clearly, not just memorize facts.

---

### Component 6: Accuracy Score (A)

**Purpose:** Combine semantic understanding with technical terminology accuracy.

**Algorithm:**

```
Accuracy = (0.6 × Similarity_Percentage) + (0.4 × Keyword_Score)

Where:
- Similarity_Percentage: SBERT neural model output (0-100%)
- Keyword_Score: Already computed (0-100%)
- Weights: 60% semantic, 40% terminology

Example:
Similarity_Score: 68.25%
Keyword_Score: 5.26%
Accuracy = (0.6 × 68.25) + (0.4 × 5.26)
         = 40.95 + 2.10
         = 43.05%
```

**Why This Formula?** 
- Prioritizes semantic understanding (60%) but ensures terminology is used (40%)
- Prevents "correct in spirit but wrong words" from scoring too high
- Prevents "right words but wrong meaning" from scoring too high

---

### Component 7: Contextual Composite Score

**Purpose:** Combine all 6 metrics into a single "context quality" score.

**Formula:**

```
Contextual Score = 0.20K + 0.15L + 0.15S + 0.20C + 0.20A + 0.10Cl

Where:
K = Keyword Coverage (0-100%)
L = Length Adequacy (0-100%)
S = Structure Quality (0-100%)
C = Completeness Score (0-100%)
A = Accuracy Score (0-100%)
Cl = Clarity Score (0-100%)

Weights (add to 100%):
- Keyword: 20% (most important for correctness)
- Completeness: 20% (depth of answer)
- Accuracy: 20% (semantic + terminology)
- Length: 15% (avoid too-brief answers)
- Structure: 15% (clarity matters)
- Clarity: 10% (nice to have but less critical)
```

**Example Calculation:**

Assume student answer to photosynthesis question:
```
Keyword_Score: 35.0%
Length_Score: 50.0%
Structure_Score: 72.5%
Completeness_Score: 40.0%
Accuracy_Score: (0.6 × 68.25) + (0.4 × 35.0) = 40.95 + 14.0 = 54.95% ≈ 55%
Clarity_Score: 60.0%

Contextual = (0.20 × 35.0) + (0.15 × 50.0) + (0.15 × 72.5) 
           + (0.20 × 40.0) + (0.20 × 55.0) + (0.10 × 60.0)
           = 7.0 + 7.5 + 10.875 + 8.0 + 11.0 + 6.0
           = 50.375% ≈ 50.38%
```

---

### Component 8: Semantic Similarity Score (SBERT)

**Purpose:** Use AI to compare the semantic meaning of student vs. model answer.

**What is SBERT?**
- "Sentence-BERT": Pre-trained neural network that converts sentences to numerical vectors (embeddings)
- Trained on billions of English text examples
- Understands that "cat is sleeping" is semantically similar to "dog is resting"
- Returns similarity as a percentage (0-100%)

**How it Works:**

1. Convert student answer to embedding vector
2. Convert model answer to embedding vector
3. Compute cosine similarity between vectors
4. Return as percentage (0-100%)

**Example Outputs:**
```
Student: "Plants use sunlight to make energy"
Model: "Photosynthesis is sunlight used by plants to create glucose"
SBERT Similarity: 72.5% ✓ High semantic match

Student: "Plants drink water and sleep at night"
Model: "Photosynthesis is the process where plants convert light energy"
SBERT Similarity: 28.3% ✗ Low semantic match
```

**Important:** SBERT alone would allow wrong answers to score high if they're topically related. That's why we combine it with deterministic scoring.

---

### Component 9: Hybrid Final Score (Before Penalties)

**Purpose:** Balance neural AI judgment with rule-based deterministic scoring.

**Formula:**

```
Hybrid Score = (0.70 × Similarity_Score) + (0.30 × Contextual_Score)

Where:
Similarity_Score: SBERT output (0-100%)
Contextual_Score: Weighted combination of 6 metrics (0-100%)
Weights: 70% trust SBERT, 30% trust context

Example:
Similarity: 68.25%
Contextual: 50.38%
Hybrid = (0.70 × 68.25) + (0.30 × 50.38)
       = 47.775 + 15.114
       = 62.889% ≈ 62.89%
```

**Why These Weights?**
- 70% SBERT: AI is very good at semantic understanding
- 30% Context: Rule-based metrics catch nuances AI might miss

---

### Component 10: Penalty & Cap Adjustments

**Problem Being Solved:**
Student answers that are topically related but factually wrong could still score high (e.g., 38-50%) using just hybrid scoring.

**Solution: Three-Layer Penalty System**

#### Layer 1: Semantic Mismatch Detection

**Condition:**
```
Similarity ≥ 60% AND Keyword < 20% AND Completeness < 35%
```

**What This Detects:**
- Answer mentions same topic (high similarity)
- But missing key terminology (low keywords)
- And incomplete explanation (low completeness)
- → Likely "sounds right but is wrong"

**Action:**
```
contextual_score × 0.40  (reduce to 40% of original value)
final_penalty = 0.35
```

**Example:**
```
Similarity: 65% (sounds relevant)
Keyword: 12% (mentions few key terms)
Completeness: 20% (covers few subpoints)
Contextual: 55%

Condition Met? ✓ Yes (65≥60, 12<20, 20<35)

Original Hybrid: (0.70 × 65) + (0.30 × 55) = 45.5 + 16.5 = 62%
After Mismatch Penalty:
  - Contextual reduced: 55% × 0.40 = 22%
  - New Hybrid: (0.70 × 65) + (0.30 × 22) = 45.5 + 6.6 = 52.1%
  - Apply final_penalty: 52.1% × 0.35 = 18.235% ≈ 18.24%
```

#### Layer 2: Mild Penalty for Low Engagement

**Condition:**
```
Keyword < 15% AND Completeness < 25%
```

**What This Detects:**
- Answer barely touches the expected content
- Missing most key terms
- Extremely incomplete

**Action:**
```
contextual_score × 0.70  (reduce to 70% of original value)
final_penalty = 0.60
```

#### Layer 3: Hard Relevance Caps

Even after all scoring, apply hard maximum caps based on completeness + keyword:

```
If completeness ≤ 20% AND keyword ≤ 25%:
  → Final score capped at 15%

If completeness ≤ 35% AND keyword ≤ 30%:
  → Final score capped at 22%

If completeness ≤ 45% AND keyword ≤ 35%:
  → Final score capped at 28%
```

**Why Hard Caps?**
- Forces very incomplete answers to score low regardless of similarity
- Prevents "wrong but topically related" from getting C-grades

**Example (Real Case):**
```
Wrong Answer Q1:
Similarity: 68.25%
Keyword: 5.26% (very low)
Completeness: 20% (low)
Contextual: Initial = 50.38%

Step 1: Check semantic mismatch?
  68.25 ≥ 60? ✓
  5.26 < 20? ✓
  20 < 35? ✓
  → Apply: contextual = 50.38 × 0.40 = 20.152
           penalty = 0.35

Step 2: Check mild penalty? (5.26 < 15? ✓ 20 < 25? ✓)
  → Already caught by semantic mismatch

Step 3: Check hard caps?
  completeness ≤ 20? ✓ (20 = 20)
  keyword ≤ 25? ✓ (5.26 < 25)
  → Apply cap: 15%

Final Score = min(52.1% × 0.35, 15%) = min(18.24%, 15%) = 15%

Result: 15% = F-Grade ✓ (instead of 38% = C-Grade ✗)
```

---

### Component 11: NLI (Natural Language Inference) Contradiction Check

**Purpose:** Detect if student answer logically contradicts the correct answer.

**How NLI Works:**
- Neural model analyzes if student_answer logically "entails", "contradicts", or is "neutral" to model_answer
- Returns probabilities for each (0-1, summing to ~1.0)

**Example:**
```
Student: "Plants absorb oxygen from soil"
Model: "Plants absorb water from soil and oxygen from air"

NLI Analysis:
- Entailment probability: 0.15 (mostly true but partial)
- Neutral probability: 0.20 (some overlap)
- Contradiction probability: 0.65 ✗ STRONG CONTRADICTION (says opposite about oxygen source)

Decision: Apply cap!
```

**Logic & Scoring:**

```
if contradiction_prob ≥ 0.65 AND contradiction > entailment:
  → Cap final score at 5.0%
  → Rationale: Logically wrong answer, even if topically related

elif entailment ≥ 0.70 AND entailment > contradiction:
  → result_confidence = 'high'
  → Rationale: Statement is logically supported

else:
  → result_confidence = 'low' (uncertain)
```

**Why This Helps:**
- Catches subtle errors that keyword matching might miss
- Example: "Photosynthesis is the process where plants absorb oxygen" 
  - Mentions all right terms (high keywords)
  - But reverses direction (plants produce oxygen, not absorb)
  - NLI detects contradiction → cap at 5%

---

## Subpoints Extraction & Matching

This is critical for completeness scoring. Let me explain with detailed examples.

### How Subpoints Are Extracted

**Input:** Model answer text

**Algorithm:**

1. **Split by Natural Delimiters**

Splits the model answer by:
- Sentence boundaries (. ! ?)
- Semicolons (;), colons (:)
- Bullet points (•), dashes (-)
- Logical conjunctions: AND, ALSO, FURTHER, MOREOVER, ADDITIONALLY

2. **Filter & Clean Each Segment**

Only keep segments with 2+ content tokens (3+ character, non-stopwords)

3. **Tokenize & Stem Each Subpoint**

Remove stopwords, apply stemming to normalize

4. **Deduplicate**

Remove duplicate subpoints while preserving order

5. **Limit to 8 Subpoints**

Cap at 8 to avoid over-segmentation

### Detailed Example

**Model Answer:**
```
"Photosynthesis is the process where plants convert light energy into chemical 
energy. The process occurs in the chloroplasts and requires water, carbon dioxide, 
and sunlight. The plant absorbs water through roots and takes in CO2 through stomata. 
Light is captured by chlorophyll. The process produces glucose as food and oxygen 
as a byproduct."
```

**Split by Delimiters:**

Raw segments:
```
1. "Photosynthesis is the process where plants convert light energy into chemical energy"
2. "The process occurs in the chloroplasts and"  
   [splits due to "and"]
3. "requires water, carbon dioxide, and sunlight"
4. "The plant absorbs water through roots and"  
   [splits due to "and"]
5. "takes in CO2 through stomata"
6. "Light is captured by chlorophyll"
7. "The process produces glucose as food and"  
   [splits due to "and"]
8. "oxygen as a byproduct"
```

**Filter by Content (≥2 tokens):**

All pass (no segments < 2 tokens)

**Tokenize & Stem (remove stopwords, stem):**

```
1. [photosynthesis, process, plant, convert, light, energy, chemical]
2. [process, occur, chloroplas]
3. [require, water, carbon, dioxide, sunlight]
4. [plant, absorb, water, root]
5. [take, co2, stomat]  [note: "in" is stopword]
6. [light, captur, chlorophyl]  [note: "by" is stopword]
7. [process, produc, glucose, food]
8. [oxygen, byproduct]
```

**Reconstruct as Readable Subpoints:**

```
1. "photosynthesis process plant convert light energy chemical"
2. "process occur chloroplas"
3. "require water carbon dioxide sunlight"
4. "plant absorb water root"
5. "take co2 stomat"
6. "light captur chlorophyl"
7. "process produc glucose food"
8. "oxygen"  [only 1 token - might filter out]
```

**Dedup & Final List:**

```
Final Subpoints (7 items):
1. "photosynthesis process plant convert light energy chemical"
2. "process occur chloroplas"
3. "require water carbon dioxide sunlight"
4. "plant absorb water root"
5. "take co2 stomat"
6. "light captur chlorophyl"
7. "process produc glucose food"
```

### How Student Answers Are Matched

**Student Answer:**
```
"Plants use sunlight and water to make glucose and oxygen"
```

**Tokenize Student Answer:**

```
Tokens: [plant, use, sunlight, water, make, glucose, oxygen]
As Set: {plant, use, sunlight, water, make, glucose, oxygen}
```

**Match Each Subpoint:**

For each subpoint, count matching tokens:

```
Subpoint 1: "photosynthesis process plant convert light energy chemical"
Tokens needed: 7
Tokens in student answer: 1 (plant)
% match: 1/7 = 14%
Threshold: 60% of 7 = 4.2 tokens needed
Result: 1 < 4.2 → NOT MATCHED ✗

Subpoint 2: "process occur chloroplas"
Tokens needed: 3
Tokens in student answer: 0
Result: 0 < 2 → NOT MATCHED ✗

Subpoint 3: "require water carbon dioxide sunlight"
Tokens needed: 5
Tokens in student answer: 2 (water, sunlight)
% match: 2/5 = 40%
Threshold: 60% of 5 = 3 tokens needed
Result: 2 < 3 → NOT MATCHED ✗

Subpoint 4: "plant absorb water root"
Tokens needed: 4
Tokens in student answer: 2 (plant, water)
Result: 2 < 3 → NOT MATCHED ✗

Subpoint 5: "take co2 stomat"
Tokens needed: 3
Tokens in student answer: 0
Result: 0 < 2 → NOT MATCHED ✗

Subpoint 6: "light captur chlorophyl"
Tokens needed: 3
Tokens in student answer: 1 (light)
Result: 1 < 2 → NOT MATCHED ✗

Subpoint 7: "process produc glucose food"
Tokens needed: 4
Tokens in student answer: 1 (glucose)
Result: 1 < 3 → NOT MATCHED ✗
```

**Result:**
```
Matched Subpoints: 0 / 7
Completeness Score: (0/7) × 100 = 0%
```

**Why 0% Completeness?**
Student mentioned concepts but didn't explain the SUBPOINTS:
- Didn't explain what photosynthesis IS
- Didn't mention where it happens
- Didn't explain inputs vs outputs clearly
- Didn't mention absorbing vs making
- Didn't mention chloroplasts, stomata, roots
- Answer too vague "make glucose" (vs "produce glucose")

---

## Real-World Examples

### Example 1: Correct Answer (High Score Expected)

**Question:** "Explain photosynthesis and its importance to life on Earth."

**Model Answer (Expected):**
```
Photosynthesis is the process by which plants, algae, and certain bacteria convert 
light energy from the sun into chemical energy stored in glucose. This process occurs 
in the chloroplasts of green plant cells. It requires three main inputs: water 
(absorbed through roots), carbon dioxide (taken from the atmosphere through stomata), 
and light energy from the sun. The process produces glucose, which serves as the 
plant's food source for energy and growth, and oxygen, which is released as a 
byproduct. Oxygen is essential for respiration in most living organisms. Therefore, 
photosynthesis is crucial for producing the oxygen we breathe and providing the 
foundation of most food chains on Earth.
```

**Student Answer:**
```
Photosynthesis is the biological process where plants convert solar energy from the 
sun into chemical energy in the form of glucose. This happens in the chloroplasts 
within plant cells. The process needs water from the soil via roots, carbon dioxide 
from the air through leaf stomata, and sunlight. It produces two main products: 
glucose for plant nutrition and energy, and oxygen which is released into the 
atmosphere. This is vital to life because animals and humans depend on the oxygen 
for respiration, and plants form the base of food chains providing energy to all 
other organisms.
```

**Scoring Analysis:**

1. **Keyword Coverage**
   - Model keywords: [photosynthesis, process, convert, energy, light, sun, chemical, glucose, chloroplasts, cells, water, roots, carbon, dioxide, atmosphere, stomata, oxygen, respiration, food, chains]
   - Student tokens: {photosynthesis, biological, process, plant, convert, solar, energy, sun, chemical, form, glucose, happen, chloroplasts, within, plant, cells, process, need, water, soil, root, carbon, dioxide, air, leaf, stomat, sunlight, produce, main, product, glucose, plant, nutrition, oxygen, release, atmosphere, vital, life, animal, human, depend, respiration, plant, form, base, food, chain, provide, energy, organism}
   - Matched: ~18/20 keywords
   - **Keyword Score: 90%** ✓

2. **Length Adequacy**
   - Model words: ~110
   - Student words: ~95
   - Ratio: 95/110 = 0.86 (within 50-100% range)
   - **Length Score: 86%** ✓

3. **Structure Quality**
   - Sentences: 5 (100% subscore)
   - Punctuation: Yes (100%)
   - Connectives: "and", "via" (67% subscore)
   - Bullets: No (60%)
   - **Structure Score: 0.30×100 + 0.25×100 + 0.25×67 + 0.20×60 = 81.75%** ✓

4. **Completeness**
   - Subpoints: 7-8 expected
   - Matched: 6-7 (mentions process, converts energy, location, inputs, outputs, oxygen importance, food chains)
   - **Completeness Score: 85%** ✓

5. **Clarity**
   - Avg sentence length: 95/5 = 19 words (near optimal 17)
   - Base: 100 - 4×|19-17| = 100 - 8 = 92%
   - Bonuses: Multiple sentences (+5), punctuation (+5),sufficient length (+5)
   - **Clarity Score: 97%** ✓

6. **Accuracy**
   - SBERT Similarity: 88% ✓
   - Keyword Score: 90%
   - Accuracy = 0.6×88 + 0.4×90 = 52.8 + 36 = 88.8%
   - **Accuracy Score: 88.8%** ✓

7. **Contextual Composite**
   - = 0.20×90 + 0.15×86 + 0.15×81.75 + 0.20×85 + 0.20×88.8 + 0.10×97
   - = 18 + 12.9 + 12.26 + 17 + 17.76 + 9.7
   - = **87.62%** ✓

8. **Hybrid Score**
   - = 0.70×88 + 0.30×87.62
   - = 61.6 + 26.286
   - = **87.886% ≈ 87.89%** ✓

9. **Penalties**
   - Semantic mismatch? 88≥60? ✓ But keyword=90≥20? ✗ NO PENALTY
   - Hard caps? Completeness=85, not in low ranges → NO CAP

10. **NLI Check**
    - Contradiction probability: 0.02 (minimal)
    - Entailment probability: 0.95 (strong agreement)
    - Result: High confidence ✓

**Final Score: 87.89% = A-Grade (12/15 marks if 15-mark question)**

**Grade Assignment:** A ✓

---

### Example 2: Wrong Answer (Should Score Low)

**Same Question**

**Student Answer:**
```
Plants absorb oxygen from the soil and use it to make energy. Photosynthesis 
happens very fast and produces water. It's important because plants need it.
```

**Scoring Analysis:**

1. **Keyword Coverage**
   - Expected keywords: [photosynthesis, process, convert, energy, light, sun, chemical, glucose, chloroplasts, water, roots, carbon, dioxide, stomata, oxygen, respiration, food]
   - Matched: [photosynthesis, energy, plant, important] ≈ 2-3 keywords
   - **Keyword Score: 13%** ✗

2. **Length**
   - Model: ~110 words
   - Student: 28 words
   - Ratio: 28/110 = 0.25 < 0.5 → clamped to 0.5
   - **Length Score: 50%** ✗

3. **Structure**
   - Sentences: 3 (100% subscore)
   - Punctuation: Yes (100%)
   - Connectives: None (0%)
   - Bullets: No (60%)
   - **Structure Score: 0.30×100 + 0.25×100 + 0.25×0 + 0.20×60 = 45%**

4. **Completeness**
   - Missed subpoints: Location (chloroplasts), Inputs (water, CO2, light distinction), Outputs clarity (says "makes water" not "makes glucose"), Importance (oxygen for respiration)
   - Matched: 0-1 / 7
   - **Completeness Score: 15%** ✗

5. **Clarity**
   - Avg: 28/3 = 9.33 words/sentence (too short, choppy)
   - Base: 100 - 4×|9.33-17| = 100 - 30.68 = 69.32%
   - Bonuses: Multiple sentences (+5), 3+ words (+5)
   - **Clarity Score: 79%**

6. **Accuracy**
   - SBERT: 42% (topically related but wrong)
   - Keyword: 13%
   - Accuracy = 0.6×42 + 0.4×13 = 25.2 + 5.2 = 30.4%
   - **Accuracy Score: 30.4%** ✗

7. **Contextual Composite**
   - = 0.20×13 + 0.15×50 + 0.15×45 + 0.20×15 + 0.20×30.4 + 0.10×79
   - = 2.6 + 7.5 + 6.75 + 3 + 6.08 + 7.9
   - = **33.83%** ✗

8. **Hybrid Score (Before Penalties)**
   - = 0.70×42 + 0.30×33.83
   - = 29.4 + 10.149
   - = **39.549%** ✗

9. **Penalties**
   - Semantic Mismatch? 42≥60? ✗ NO
   - Mild Penalty? 13<15? ✓ AND 15<25? ✓ YES
     - Contextual reduced: 33.83 × 0.70 = 23.68
     - Penalty: 0.60
   - New Hybrid: 0.70×42 + 0.30×23.68 = 29.4 + 7.104 = 36.504%
   - After penalty: 36.504 × 0.60 = **21.90%**
   
   - Hard Caps? Completeness=15≤20? ✓ AND Keyword=13≤25? ✓
     - Cap applied: 15%
   - Final: min(21.90, 15) = **15%** ✗

10. **NLI Check**
    - "absorb oxygen" vs "produce oxygen"
    - Contradiction probability: 0.72 ✗
    - Applies NLI cap: 5%
    - Final: min(15%, 5%) = **5%** 

**Final Score: 5% = F-Grade (0.75/15 marks)**

---

## Quality Assurance & Penalties

### Why Penalties Matter

Without penalties, the wrong answer would score:
- Raw hybrid: 39.5%
- With mild penalty only: 21.9%
- **With hard cap: 15%** (prevented C-grade)
- **With NLI: 5%** (prevented any credit for wrong logic)

### Summary of All Adjustment Mechanisms

| Mechanism | Trigger | Effect | Purpose |
|-----------|---------|--------|---------|
| **Semantic Mismatch** | High similarity (≥60%) + Low keywords (<20%) + Low completeness (<35%) | Reduce contextual by 40%, multiply final by 0.35 | Catch "sounds right but factually wrong" |
| **Mild Penalty** | Low keywords (<15%) + Low completeness (<25%) | Multiply contextual by 0.70, final by 0.60 | Penalize barely-touched answers |
| **Hard Cap 15%** | Completeness ≤20% AND Keyword ≤25% | Final score ≤15% | Prevent high scores for incomplete answers |
| **Hard Cap 22%** | Completeness ≤35% AND Keyword ≤30% | Final score ≤22% | Prevent above-passing grades for weak answers |
| **Hard Cap 28%** | Completeness ≤45% AND Keyword ≤35% | Final score ≤28% | Prevent passing grades for partial answers |
| **NLI Contradiction** | Contradiction probability ≥65% | Final score ≤5% | Catch logically wrong statements |

### Grade Scale

```
Score Range     Grade    Interpretation
90-100%         A        Excellent - comprehensive, accurate, well-articulated
80-89%          B        Good - mostly correct and complete, minor gaps
70-79%          C        Satisfactory - covers main points but incomplete
60-69%          D        Needs Improvement - significant gaps in understanding
Below 60%       F        Fail - major conceptual errors or insufficient coverage
```

---

## Complete Data Flow Example

Let me trace one complete evaluation from start to finish:

**Input:**
```json
{
  "student_answer": "Plants use sunlight.",
  "model_answer": "Photosynthesis is the process...[110 words]",
  "question_text": "Explain photosynthesis.",
  "marks": 15
}
```

**Processing Pipeline:**

```
Step 1: Text Normalization
  student: "plants use sunlight"
  model: "photosynthesis is the process..." [normalized]

Step 2: SBERT Similarity
  Input: Both answers
  Model: Converts to embeddings
  Cosine similarity: 0.35 → 35%

Step 3: Context Components
  - Tokenize both answers
  - Extract keywords from model
  - Count word overlap → keyword_score: 10%
  - Count words → length_score: 25% (too brief)
  - Analyze structure → structure_score: 40%
  - Check subpoints → completeness: 5%
  - Analyze clarity → clarity_score: 55%
  - Accuracy = 0.6×35 + 0.4×10 = 25%

Step 4: Contextual Composite
  Context = 0.20×10 + 0.15×25 + 0.15×40 + 0.20×5 + 0.20×25 + 0.10×55
          = 2 + 3.75 + 6 + 1 + 5 + 5.5
          = 23.25%

Step 5: Hybrid (Before Penalties)
  Hybrid = 0.70×35 + 0.30×23.25
         = 24.5 + 6.975
         = 31.475% ≈ 31.48%

Step 6: Penalties
  Semantic Mismatch? 35≥60? ✗ NO
  Mild Penalty? 10<15? ✓ AND 5<25? ✓ YES
    - Context: 23.25 × 0.70 = 16.275
    - Hybrid: 0.70×35 + 0.30×16.275 = 24.5 + 4.88 = 29.38%
    - Final penalty: 29.38 × 0.60 = 17.63%

Step 7: Hard Caps
  Completeness=5≤20? ✓ AND Keyword=10≤25? ✓
  Cap: 15%
  Result: min(17.63%, 15%) = 15%

Step 8: NLI Check
  Contradiction: 0.25 (low)
  Entailment: 0.30 (low)
  No NLI penalty

Step 9: Marks Conversion
  obtained = (15 / 100) × 15 = 2.25 marks

Step 10: Grade Assignment
  15% = F-Grade
```

**Final Output:**
```json
{
  "similarity_score": 35.0,
  "contextual_score": 16.28,
  "final_score_pct": 15.0,
  "marks_allocated": 15,
  "obtained_marks": 2.25,
  "grade": "F",
  "keyword_score": 10.0,
  "completeness_score": 5.0,
  "matched_keywords": ["plant", "sunlight"],
  "matched_subpoints": [],
  "nli_contradiction": 0.25,
  "confidence": "low",
  "feedback": "Answer is very brief and missing key concepts. Include explanation of what photosynthesis is, where it occurs, what inputs are needed, and what outputs are produced.",
  "weaknesses": ["Meaning does not sufficiently align", "Missing important keywords", "Too brief"],
  "suggestions": ["Explain the process fully", "Include all key terms"]
}
```

---

## FAQ for Supervisors

**Q: Why do you use 70% SBERT and 30% context instead of 50-50?**
A: AI neural models are very accurate at semantic matching, but they can miss domain-specific nuances. 70-30 balances "AI is usually right" with "don't trust it completely." We empirically found this prevents wrong answers from scoring too high.

**Q: What if a student uses synonyms like "energy" instead of "ATP"?**
A: SBERT semantic similarity handles this. It understands "glucose is food" and "glucose is energy source" are similar. Plus, keyword matching has leeway—if 60% of subpoint keywords match, the subpoint counts.

**Q: Can a student get full marks for a short but perfect answer?**
A: Length matters because exams test depth. A one-sentence answer, even if semantically correct, gets capped by the length adequacy component (50% minimum if < 50% of model). So maximum without full length is ~70-80%.

**Q: What if the model answer is wrong?**
A: The system only learns from the model answer provided. If the model answer itself is incorrect, the student answers will be evaluated against incorrect content. This is why careful model answer preparation is critical.

**Q: How does the system handle different question types (short answer vs essay)?**
A: The formulas are agnostic to length. A 3-word short answer answer and a 500-word essay both use the same 6-component model. Shorter answers might naturally score lower due to length/completeness caps, which is appropriate.

**Q: Can two identical answers score differently?**
A: No. Given the same student answer, model answer, and question text, the scoring is deterministic (except NLI model which might have minor variations on CPU vs GPU).

**Q: What happens if the student answer is blank?**
A: The evaluator requires non-empty answers. A blank submission returns: final_score_pct: 0%, confidence: low, feedback explaining answer is missing.

---

## Conclusion

The evaluation system uses a **principled, multi-layered approach** that:

1. **Leverages AI strength** (SBERT semantic similarity at 70%)
2. **Adds rule-based verification** (keyword, completeness, structure at 30%)
3. **Prevents gaming** (penalties for topically-related but wrong answers)
4. **Adds logic checks** (NLI for contradictions)
5. **Provides transparency** (all 15+ output fields show reasoning)

This prevents the documented issue where "wrong answer scores C-grade (38%)" by ensuring completeness, keyword coverage, and logical consistency all must be present for high scores.

