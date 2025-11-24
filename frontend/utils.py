import base64
from pathlib import Path

from frontend.constants import LOGO_PATH


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def build_logo_before_title_html(title):
    logo_base64 = get_base64_image(LOGO_PATH)
    return f"""
        <style>
        .logo-title-container {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .logo-title-container img {{
            width: 60px;
            height: auto;
        }}
        .logo-title-container h1 {{
            margin: 0;
            font-size: 2.5rem;
        }}
        </style>
    
        <div class="logo-title-container">
            <img src="data:image/jpeg;base64,{logo_base64}" alt="Logo">
            <h1>{title}</h1>
        </div>
    """
