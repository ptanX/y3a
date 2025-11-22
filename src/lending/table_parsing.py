import json
import pathlib
from typing import Union

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


# Retrieve and encode the PDF byte
def extract_information(filepath: Union[str, pathlib.Path]) -> dict:
    if isinstance(filepath, str):
        filepath = pathlib.Path(filepath)
    client = genai.Client()
    prompt = """
    Từ file PDF đã gửi lên, trong đó các trang là bộ phận hợp thành của một bảng báo cáo tài chính lớn duy nhất, hãy trích xuất dữ liệu của bảng đó thành định dạng JSON.

    YÊU CẦU CẤU TRÚC JSON:
    1. Sử dụng giá trị tại ngày cuối kỳ (ngày có giá trị lớn nhất, thường là 31/12/YYYY, 20YY).
    2. Chuyển đổi tất cả các giá trị số sang dạng số nguyên (integer/number), loại bỏ dấu phân cách hàng nghìn. Giá trị của toàn bộ ô trong ngoặc "()" được chuyển thành số âm. Giá trị của toàn bộ ô là "-" được chuyển thành "null".
    3. Mỗi đối tượng JSON (object) phải có 3 attributes:
        * "description": Tên mục tiếng Việt nguyên bản từ cột Danh mục, loại bỏ phần công thức tính toán (ví dụ: "(100=110+130)", "(400=410)", v.v.).
        * "name": Tên tiếng Anh tương ứng với mục tiếng Việt (sử dụng snake_case).
        * "value": Giá trị số cuối cùng đã được chuyển đổi tại ngày cuối kỳ.
    4. Câu trả lời chỉ trả về JSON hợp lệ, không cần giải thích thêm.

    Hãy đảm bảo tính chính xác, đầy đủ và trình bày rõ ràng để thuận tiện cho việc phân tích sau này.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type="application/pdf",
            ),
            prompt,
        ],
    )

    response_json = json.loads(
        response.text.replace("```json", "").replace("```", "").strip()
    )
    print(response_json)

    with open(str(filepath).rsplit(".", 1)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump(response_json, f, ensure_ascii=False, indent=2)

    return response_json
