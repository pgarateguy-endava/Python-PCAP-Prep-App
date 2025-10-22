# PCAP Quiz App

A simple interactive quiz application to help you prepare for the PCAP (Python Certified Associate Programmer) certification exam.

## Requirements

- Python 3.x
- Streamlit

## Installation

1. Clone this repository:
```bash
git clone https://github.com/pgarateguy-endava/Python-PCAP-Prep-App.git
cd Python-PCAP-Prep-App
```

2. Install the required package:
```bash
pip3 install streamlit
```

## Usage

To run the application:
```bash
python3 -m streamlit run exam_web.py
```

The application will start and open in your default web browser. If it doesn't open automatically, you can access it at the local URL shown in the terminal (usually http://localhost:8501).

## Questions Format

The questions are stored in `questions.json` file. Here's an example of the format:

```json
[
  {
    "id": 1,
    "question": "What is the output of print(type((1,2,3))) in Python?",
    "options": ["<class 'list'>", "<class 'tuple'>", "<class 'set'>", "<class 'dict'>"],
    "answer_index": 1,
    "explanation": "Parentheses create a tuple; lists use square brackets []."
  }
]
```

## Customization

You can modify the `questions.json` file to add your own PCAP practice questions. Make sure to follow the JSON format shown above.
