import json, random, time
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="PCAP Quiz", page_icon="🧠", layout="centered")

def load_questions(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("The JSON must contain a list of questions.")
        for q in data:
            if not all(k in q for k in ("question", "options", "answer_index")):
                raise ValueError("Invalid question: missing 'question', 'options', or 'answer_index'.")
            if not isinstance(q["options"], list) or len(q["options"]) == 0:
                raise ValueError("Each question must have non-empty 'options'.")
            
            # Normalize answer_index to always be a list
            if isinstance(q["answer_index"], int):
                q["answer_index"] = [q["answer_index"]]
            elif not isinstance(q["answer_index"], list):
                raise ValueError("The 'answer_index' must be an integer or list of integers.")
            
            # Validate all indices
            for idx in q["answer_index"]:
                if not (0 <= idx < len(q["options"])):
                    raise ValueError(f"The 'answer_index' {idx} is out of range for a question.")
        return data
    
ss = st.session_state
ss.setdefault("started", False)
ss.setdefault("index", 0)
ss.setdefault("score", 0)
ss.setdefault("answers", [])
ss.setdefault("order", [])
ss.setdefault("t0", None)

st.title("🧠 PCAP Cert Quiz")
st.caption("Load questions from JSON. Ultra simple practice tool.")

json_path = Path(st.sidebar.text_input("JSON Path", "questions.json"))
limit = st.sidebar.number_input("Question Limit", min_value=0, value=0, step=1)
shuffle = st.sidebar.checkbox("Shuffle Questions", value=True)
reset_btn = st.sidebar.button("🔄 Reset")

def reset_state():
    ss.started = False
    ss.index = 0
    ss.score = 0
    ss.answers = []
    ss.order = []
    ss.t0 = None

if reset_btn:
    reset_state()
    st.rerun()

def start_quiz():
    qs = load_questions(json_path)
    if shuffle:
        random.shuffle(qs)
    if limit and limit > 0:
        qs = qs[:limit]
    if not qs:
        st.warning("No questions to display. Check your JSON file or limit setting.")
        return
    ss.order = qs
    ss.started = True
    ss.index = 0
    ss.score = 0
    ss.answers = []
    ss.t0 = time.time()

def render_results():
    qs = ss.order
    elapsed = time.time() - ss.t0 if ss.t0 else 0.0
    total = len(qs)
    pct = (ss.score/total)*100 if total else 0

    st.header("Results")
    st.metric("Score", f"{ss.score}/{total}", f"{pct:.1f}%")
    st.write(f"⏱️ Time: {elapsed:.1f} s")

    with st.expander("Detailed Review", expanded=True):
        L = min(len(ss.answers), len(qs))
        for j in range(L):
            a = ss.answers[j]
            qq = qs[j]
            st.markdown(f"**{j+1}. {qq['question']}**")
            
            status = "✔️ Correct" if a["correct"] else ("⏭️ Skipped" if a["chosen"] is None else "❌ Incorrect")
            st.write(status)
            
            # Show correct answer(s)
            correct_answers = [qq['options'][idx] for idx in qq['answer_index']]
            if len(correct_answers) == 1:
                st.write(f"Correct answer: **{correct_answers[0]}**")
            else:
                st.write(f"Correct answers: **{', '.join(correct_answers)}**")
            
            # Show user's answer if incorrect
            if a["chosen"] is not None and not a["correct"]:
                if isinstance(a["chosen"], list):
                    user_answers = [qq['options'][idx] for idx in a["chosen"]]
                    st.write(f"Your answers: {', '.join(user_answers)}")
                else:
                    st.write(f"Your answer: {qq['options'][a['chosen']]}")
            
            if "explanation" in qq and qq["explanation"]:
                st.info(qq["explanation"])

    cols = st.columns(2)
    with cols[0]:
        if st.button("Try Again 🔁", use_container_width=True):
            start_quiz()
            st.rerun()
    with cols[1]:
        if st.button("Back to Start ⏹️", use_container_width=True):
            reset_state()
            st.rerun()

# ---- UI ----
if not ss.started:
    st.write("Upload or edit your **questions.json** and click **Start**.")
    if st.button("▶️ Start"):
        try:
            start_quiz()
            if ss.started:
                st.rerun()
        except Exception as e:
            st.error(f"Error reading JSON: {e}")
else:
    qs = ss.order
    i = ss.index
    total = len(qs)

    if i >= total:
        render_results()
    else:
        q = qs[i]
        st.progress(i/max(total, 1))
        st.subheader(f"Question {i+1} of {total}")
        
        # Display question with proper code formatting
        question_lines = q["question"].split('\n')
        question_text = []
        code_block = []
        in_code = False
        
        for line in question_lines:
            # Detect if line looks like code
            if line.strip() and (
                line.startswith(('def ', 'class ', 'import ', 'from ', 'for ', 'while ', 'if ', 'try:', 'except', 'print(')) or
                '=' in line or line.strip().startswith(('    ', '\t'))
            ):
                if not in_code and question_text:
                    st.write(' '.join(question_text))
                    question_text = []
                in_code = True
                code_block.append(line)
            else:
                if in_code and code_block:
                    st.code('\n'.join(code_block), language='python')
                    code_block = []
                    in_code = False
                if line.strip():
                    question_text.append(line)
        
        # Display remaining content
        if question_text:
            st.write(' '.join(question_text))
        if code_block:
            st.code('\n'.join(code_block), language='python')

        # Determine if this is a multi-answer question
        is_multi = len(q["answer_index"]) > 1
        
        if is_multi:
            st.info(f"📝 Select {len(q['answer_index'])} answers")
            choices = []
            for idx, option in enumerate(q["options"]):
                if st.checkbox(option, key=f"choice_{i}_{idx}"):
                    choices.append(idx)
        else:
            choice = st.radio("Choose an option:", q["options"], index=None, key=f"choice_{i}")
            choices = [q["options"].index(choice)] if choice is not None else None

        cols = st.columns(2)
        with cols[0]:
            if st.button("⏭️ Skip", use_container_width=True):
                ss.answers.append({
                    "id": q.get("id"), 
                    "chosen": None, 
                    "correct": False, 
                    "correct_index": q["answer_index"]
                })
                ss.index += 1
                st.rerun()
        with cols[1]:
            if st.button("Answer ✅", use_container_width=True, disabled=(choices is None or len(choices) == 0)):
                # Check if answer is correct
                correct = set(choices) == set(q["answer_index"]) if choices else False
                
                if correct:
                    ss.score += 1
                
                ss.answers.append({
                    "id": q.get("id"), 
                    "chosen": choices if is_multi else (choices[0] if choices else None), 
                    "correct": correct, 
                    "correct_index": q["answer_index"]
                })
                ss.index += 1
                st.rerun()

        if st.button("Finish Now 🏁"):
            ss.index = total
            st.rerun()