import sys
from hwp5.dataio import HWP5File
import os

def extract_text_from_hwp(file_path):
    with open(file_path, "rb") as f:
        hwp = HWP5File(f)
        text = ""
        for section in hwp.bodytext:
            for para in section:
                text += para.text + "\n"
        return text

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("사용법: python convert_hwp_to_txt.py <input.hwp> <output.txt>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    if not os.path.exists(input_path):
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)

    try:
        result = extract_text_from_hwp(input_path)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 변환 완료: {output_path}")
    except Exception as e:
        print(f"❌ 변환 중 오류 발생: {str(e)}")
        sys.exit(1)