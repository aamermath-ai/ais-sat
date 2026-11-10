# Emir

Free adaptive Digital SAT practice for AIS students.
Mathematics Department, American International School.

**Open the app:** see the GitHub Pages link in this repository's About section.

## What it does
- Practice the whole syllabus, Reading & Writing, or Math, optionally focused on one of the eight Digital SAT content domains.
- Questions adapt to each answer: correct answers raise the difficulty, misses lower it.
- Every question has a step-by-step solution and a key idea, shown automatically after a wrong answer.
- Shows practice score estimates (200–800 per section), domain mastery and recent sets.

Progress is saved in the student's own browser on their own device. Nothing is sent to a server.

## About the questions
College Board does not release past SAT papers for reuse. The questions in `questions.json` are original practice items written to College Board's published Digital SAT content specifications. For official practice, use [Bluebook](https://bluebook.collegeboard.org/) and the [SAT Suite Question Bank](https://satsuitequestionbank.collegeboard.org/).

## Adding questions
Edit `questions.json` and add an object to the list:

```json
{
  "id": "m-al-07",
  "section": "math",
  "domain": "Algebra",
  "skill": "Linear equations in one variable",
  "difficulty": 2,
  "type": "mc",
  "stem": "If 4x − 3 = 13, what is x?",
  "choices": ["4", "2.5", "16", "10"],
  "answer": 0,
  "explanation": "Add 3, then divide by 4.",
  "steps": ["4x − 3 = 13", "Add 3: 4x = 16", "Divide by 4: x = 4"],
  "key": "Undo operations in reverse order.",
  "source": "AIS Mathematics Department"
}
```

- `section`: `"rw"` or `"math"`
- `domain`: Information and Ideas, Craft and Structure, Expression of Ideas, Standard English Conventions, Algebra, Advanced Math, Problem-Solving and Data Analysis, or Geometry and Trigonometry
- `difficulty`: 1 (easy), 2 (medium) or 3 (hard)
- `type`: `"mc"` (multiple choice; `answer` is the index of the correct choice, starting at 0) or `"spr"` (type-in; `answer` is the number or fraction as text)
- Optional: `passage`, `table`, `steps`, `key`, `skill`, `source`

Choices are shuffled for students, so the correct one can be listed first.
