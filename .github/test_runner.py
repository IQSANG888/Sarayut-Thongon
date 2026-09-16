import os
import re
import subprocess
import sys


def normalize_text(text):
    """ตัดสัญลักษณ์ ตัวพิมพ์เล็ก-ใหญ่ และเว้นวรรคส่วนเกิน"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[!.,:="\'\(\)]', " ", text)
    return " ".join(text.split())


def extract_numbers(text):
    """ดึงตัวเลขทั้งหมดจากผลลัพธ์ของนักเรียน"""
    if not text:
        return []
    return [float(n) for n in re.findall(r"[-+]?\d*\.\d+|\d+", text)]


def run_student_code(filename, input_data):
    """สั่งรันโค้ดนักเรียน รองรับทั้งมีและไม่มี .py"""
    target_file = filename
    if not os.path.exists(target_file) and not target_file.endswith(".py"):
        target_file = filename + ".py"

    if not os.path.exists(target_file):
        return None, "File Not Found"

    try:
        process = subprocess.run(
            [sys.executable, target_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=5,
        )
        return process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return None, "Timeout (โปรแกรมวนลูปไม่จบ)"
    except Exception as e:
        return None, str(e)


# =========================================================
# เกณฑ์การตรวจยืดหยุ่นแยกรายข้อ (คะแนนเต็มข้อละ 4 คะแนน)
# =========================================================


def grade_exam_1(output, stderr, test_case):
    """ข้อ 1: พื้นที่สามเหลี่ยม (0.5 * b * h)"""
    expected = test_case["expected"]
    b, h = test_case["b"], test_case["h"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.01 for n in nums):
        return 1.0  # คำนวณถูกต้องได้เต็ม
    elif any(abs(n - (b * h)) < 0.01 for n in nums):
        return 0.5  # คำนวณ b * h ถูกแต่ลืมคูณ 0.5
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


def grade_exam_2(output, stderr, test_case):
    """ข้อ 2: ตรวจเลขคู่ / เลขคี่ (Even / Odd)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์คำว่า Even/Odd ตรงตามเงื่อนไข
    elif "even" in norm_out or "odd" in norm_out:
        return 0.5  # มีคำว่า Even หรือ Odd ในผลลัพธ์
    return 0.0


def grade_exam_3(output, stderr, test_case):
    """ข้อ 3: ตรวจสอบผลสอบ (Pass / Fail)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)

    if expected in norm_out:
        return 1.0  # พิมพ์ Pass/Fail ถูกต้อง
    elif "pass" in norm_out or "fail" in norm_out:
        return 0.5  # พิมพ์คำตอบกลุ่มผลสอบออกมาได้
    return 0.0


def grade_exam_4(output, stderr, test_case):
    """ข้อ 4: ตัดเกรด 5 ระดับ (A, B, C, D, F)"""
    expected = test_case["expected"].lower()
    norm_out = normalize_text(output)
    words = norm_out.split()

    if expected in words or norm_out == expected:
        return 1.0  # ได้เกรดตรงตามคะแนน
    elif any(g in words for g in ["a", "b", "c", "d", "f"]):
        return 0.5  # แสดงเกรดตัวใดตัวหนึ่งออกมาได้
    return 0.0


def grade_exam_5(output, stderr, test_case):
    """ข้อ 5: ราคาตั๋วสวนสนุก (<12: 50 | 12-59: 100 | >=60: 0)"""
    expected = test_case["expected"]
    nums = extract_numbers(output)

    if any(abs(n - expected) < 0.01 for n in nums):
        return 1.0  # แสดงราคาตั๋วถูกต้อง
    elif any(n in [0, 50, 100] for n in nums):
        return 0.5  # แสดงราคาตัวใดตัวหนึ่งในเรตตั๋ว
    elif len(nums) > 0:
        return 0.25  # มีการแสดงผลตัวเลขออกมา
    return 0.0


# =========================================================
# ชุดข้อมูลทดสอบ (Test Cases สำหรับ Examination_1.py - Examination_5.py)
# =========================================================
EXAMS = {
    "Examination_1.py": {
        "grader": grade_exam_1,
        "cases": [
            {"input": "10\n5\n", "expected": 25.0, "b": 10, "h": 5},
            {"input": "8\n4\n", "expected": 16.0, "b": 8, "h": 4},
            {"input": "15\n6\n", "expected": 45.0, "b": 15, "h": 6},
            {"input": "7\n3\n", "expected": 10.5, "b": 7, "h": 3},
        ],
    },
    "Examination_2.py": {
        "grader": grade_exam_2,
        "cases": [
            {"input": "4\n", "expected": "Even"},
            {"input": "7\n", "expected": "Odd"},
            {"input": "0\n", "expected": "Even"},
            {"input": "15\n", "expected": "Odd"},
        ],
    },
    "Examination_3.py": {
        "grader": grade_exam_3,
        "cases": [
            {"input": "80\n", "expected": "Pass"},
            {"input": "45\n", "expected": "Fail"},
            {"input": "50\n", "expected": "Pass"},
            {"input": "49\n", "expected": "Fail"},
        ],
    },
    "Examination_4.py": {
        "grader": grade_exam_4,
        "cases": [
            {"input": "85\n", "expected": "A"},
            {"input": "75\n", "expected": "B"},
            {"input": "65\n", "expected": "C"},
            {"input": "55\n", "expected": "D"},
        ],
    },
    "Examination_5.py": {
        "grader": grade_exam_5,
        "cases": [
            {"input": "10\n", "expected": 50},
            {"input": "25\n", "expected": 100},
            {"input": "65\n", "expected": 0},
            {"input": "12\n", "expected": 100},
        ],
    },
}

# =========================================================
# ประมวลผลและสร้าง Markdown สรุปคะแนน
# =========================================================
total_score = 0.0
summary_rows = []

for exam_name, exam_data in EXAMS.items():
    grader = exam_data["grader"]
    cases = exam_data["cases"]

    exam_score = 0.0
    passed_cases = 0.0

    for case in cases:
        stdout, stderr = run_student_code(exam_name, case["input"])
        if stdout is not None:
            score = grader(stdout, stderr, case)
            exam_score += score
            if score >= 1.0:
                passed_cases += 1.0
            elif score > 0:
                passed_cases += 0.5

    final_exam_score = min(4.0, round(exam_score, 1))
    total_score += final_exam_score

    if final_exam_score >= 4.0:
        status = "🟢 ผ่าน"
    elif final_exam_score > 0:
        status = "🟡 ผ่านบางส่วน"
    else:
        status = "❌ ไม่ผ่าน"

    score_display = (
        f"{int(final_exam_score)}"
        if final_exam_score.is_integer()
        else f"{final_exam_score}"
    )
    passed_display = (
        f"{int(passed_cases)}"
        if passed_cases.is_integer()
        else f"{passed_cases}"
    )

    summary_rows.append(
        f"| `{exam_name}` | {status} | {passed_display}/4 เคส | {score_display} / 4 |"
    )

final_total_display = (
    f"{int(total_score)}" if total_score.is_integer() else f"{total_score}"
)

markdown_summary = f"""
## 📊 สรุปผลการสอบวิชาเขียนโปรแกรม

| ข้อสอบ | สถานะการตรวจ | ผ่าน Test Cases | คะแนนที่ได้ |
| :--- | :--- | :--- | :--- |
""" + "\n".join(summary_rows) + f"""

### 🎯 คะแนนรวมทั้งหมด: {final_total_display} / 20 คะแนน
"""

print(markdown_summary)

github_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
if github_summary_path:
    with open(github_summary_path, "a", encoding="utf-8") as f:
        f.write(markdown_summary)
