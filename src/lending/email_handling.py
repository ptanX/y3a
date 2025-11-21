import email
import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.lending.constant import REQUIRED_EXTRACTION_FIELDS


def build_validation_table_html(document_id, data):
    """
    Build an HTML table from validation results data

    Args:
        document_id: Document ID
        data: Dictionary containing validation results

    Returns:
        HTML string with styled table
    """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f5f5f5;
                padding: 0;
                margin: 0;
            }
            .container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 20px;
            }
            .content {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #667eea;
                margin-top: 0;
                font-size: 24px;
            }
            .intro {
                margin-bottom: 30px;
                color: #555;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background-color: white;
                margin: 20px 0;
            }
            th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 8px;
                text-align: left;
                font-weight: bold;
                border: 1px solid #ddd;
                font-size: 13px;
            }
            td {
                padding: 10px 8px;
                border: 1px solid #ddd;
                font-size: 13px;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f0f0f0;
            }
            .field-name {
                font-weight: bold;
                color: #333;
            }
            .status-true {
                color: #22c55e;
                font-weight: bold;
            }
            .status-false {
                color: #ef4444;
                font-weight: bold;
            }
            .database-value {
                color: #333;
                font-weight: 500;
            }
            .summary {
                background: #f0f4ff;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #667eea;
            }
            .footer {
                text-align: center;
                color: white;
                margin-top: 20px;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
            """ + f"""
                <h1>[DocumentID={document_id}] Validation Results Report</h1>
                <div class="intro">
                    <p>This report contains the validation results for document data verification against the database.</p>
                </div>
    """

    # Calculate summary statistics
    total_fields = len(data['results'])
    consistent_count = sum(1 for r in data['results'] if r['validation_result']['is_consistent_across_doc'])
    match_count = sum(1 for r in data['results'] if r['validation_result']['is_match_database'])

    html += f"""
                <div class="summary">
                    <strong>Summary:</strong> {total_fields} fields validated | 
                    {consistent_count}/{total_fields} consistent across documents | 
                    {match_count}/{total_fields} match database
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Field Name</th>
    """

    # Get all unique document names for headers
    all_docs = set()
    for result in data['results']:
        for doc in result['origin_docs']:
            all_docs.add(doc['name'])

    # Add headers for each document
    for doc_name in sorted(all_docs):
        html += f"                            <th>{doc_name.replace('_', ' ').title()}</th>\n"

    html += """                            <th>Database Value</th>
                            <th>Consistent</th>
                            <th>Match DB</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    # Add rows
    for result in data['results']:
        html += "                        <tr>\n"

        # Field name column
        html += f"                            <td class='field-name'>{result['field_name']}</td>\n"

        # Create a dict for quick lookup of document values
        doc_values = {doc['name']: doc['value'] for doc in result['origin_docs']}

        # Add columns for each document
        for doc_name in sorted(all_docs):
            value = doc_values.get(doc_name, '-')
            html += f"                            <td>{value}</td>\n"

        # Database value column
        db_value = result.get('database_value', '-')
        html += f"                            <td class='database-value'>{db_value}</td>\n"

        # Consistent across docs column
        is_consistent = result['validation_result']['is_consistent_across_doc']
        consistent_class = 'status-true' if is_consistent else 'status-false'
        consistent_text = '✓ Yes' if is_consistent else '✗ No'
        html += f"                            <td class='{consistent_class}'>{consistent_text}</td>\n"

        # Match database column
        is_match = result['validation_result']['is_match_database']
        match_class = 'status-true' if is_match else 'status-false'
        match_text = '✓ Yes' if is_match else '✗ No'
        html += f"                            <td class='{match_class}'>{match_text}</td>\n"

        html += "                        </tr>\n"

    html += """                    </tbody>
                </table>

                <p style="margin-top: 30px; color: #666; font-size: 14px;">
                    <strong>Note:</strong> Please review any fields marked with ✗ for inconsistencies.
                </p>
            </div>
            <div class="footer">
                <p>© 2025 RAWIQ Report System. Generated automatically.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html


def build_validation_table_text(data):
    """
    Build a plain text table from validation results data for email fallback
    """
    lines = []
    lines.append("VALIDATION RESULTS REPORT")
    lines.append("=" * 100)

    # Summary
    total_fields = len(data['results'])
    consistent_count = sum(1 for r in data['results'] if r['validation_result']['is_consistent_across_doc'])
    match_count = sum(1 for r in data['results'] if r['validation_result']['is_match_database'])

    lines.append(f"\nSummary: {total_fields} fields validated")
    lines.append(f"Consistent across documents: {consistent_count}/{total_fields}")
    lines.append(f"Match database: {match_count}/{total_fields}")
    lines.append("")

    for result in data['results']:
        lines.append(f"\nField: {result['field_name']}")
        lines.append("-" * 100)

        # Origin documents
        lines.append("Origin Documents:")
        for doc in result['origin_docs']:
            lines.append(f"  - {doc['name']}: {doc['value']}")

        # Database value
        lines.append(f"\nDatabase Value: {result['database_value']}")

        # Validation results
        is_consistent = result['validation_result']['is_consistent_across_doc']
        is_match = result['validation_result']['is_match_database']

        lines.append(f"Consistent Across Docs: {'✓ Yes' if is_consistent else '✗ No'}")
        lines.append(f"Match Database: {'✓ Yes' if is_match else '✗ No'}")
        lines.append("")

    return "\n".join(lines)


def send_validation_email(document_id, sender_email, sender_password, recipient_email, validation_data, subject=None):
    """
    Send validation results as a pretty formatted email

    Args:
        document_id: Document ID
        sender_email: Your email address
        sender_password: Your email password or app-specific password
        recipient_email: Recipient's email address
        validation_data: Dictionary containing validation results
        subject: Optional custom subject line
    """
    # Generate subject if not provided
    if not subject:
        total_fields = len(validation_data['results'])
        issues = sum(1 for r in validation_data['results']
                     if not r['validation_result']['is_consistent_across_doc']
                     or not r['validation_result']['is_match_database'])
        subject = f"RAWIQ Validation Report: {total_fields} Fields Validated"
        if issues > 0:
            subject += f" ({issues} issues found)"

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_email)

    # Create plain text and HTML versions
    body_text = build_validation_table_text(validation_data)
    body_html = build_validation_table_html(document_id, validation_data)

    part1 = MIMEText(body_text, 'plain')
    part2 = MIMEText(body_html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    # Send email
    try:
        # For Gmail (change for other providers)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✓ Validation email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False


def execute(document_id, validation_data, email_input=None):
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    RECIPIENT_EMAIL = ["vanhci52@gmail.com", "nguyenthaibinhbk@gmail.com"]
    if email_input is not None:
        RECIPIENT_EMAIL.append(email_input)

    # Send the validation email
    send_validation_email(
        document_id,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD,
        recipient_email=RECIPIENT_EMAIL,
        validation_data=validation_data
    )


def build_lending_content(**kwargs):
    recipient_name = kwargs.get("recipient_name")
    customer_name = kwargs.get("customer_name")
    document_id = kwargs.get("document_id")
    verification_time = kwargs.get("verification_time")
    total_fields = kwargs.get("total_fields")
    document_status = kwargs.get("document_status")
    document_categories = kwargs.get("document_categories")
    detail_url = kwargs.get("detail_url")

    categories_html = ""
    for category in document_categories:
        documents = category.get('documents', '')

        # Build documents list
        document_type_name = category.get('document_type_name', '')
        document_html = ""
        for doc in documents:
            name = doc.get('name', '')
            quantity = doc.get('quantity', '')
            document_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;">{name}</td>
                        <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{quantity}</td>
                    </tr>
                """

        if document_html:
            categories_html += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; vertical-align: top; font-weight: bold;" rowspan="{len(documents)}">{document_type_name}</td>
                        {document_html.split('</tr>', 1)[0].replace('<tr>', '')}
                    </tr>
                """
            # Add remaining rows
            remaining_rows = document_html.split('</tr>')[1:]
            for row in remaining_rows:
                if row.strip():
                    categories_html += row + "</tr>"

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    border: 1px solid #ddd;
                    text-align: left;
                }}
                th {{
                    background-color: #f4f4f4;
                    font-weight: bold;
                }}
                .header {{
                    margin-bottom: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <p>Kính gửi anh/chị <strong>{recipient_name}</strong></p>
                </div>

                <p>Hệ thống AgentDocCheck đã hoàn tất kiểm tra và đối chiếu hồ sơ doanh nghiệp <strong>{customer_name}</strong></p>

                <p>Dưới đây là thông tin tổng quan dữ liệu sau khi phân tích báo cáo của khách hàng xin vay vốn</p>

                <h3>Thông tin tổng quan</h3>
                <table>
                    <tr>
                        <td>Tên Khách hàng</td>
                        <td>{customer_name}</td>
                    </tr>
                    <tr>
                        <td>Số Hồ Sơ Vay</td>
                        <td>{document_id}</td>
                    </tr>
                    <tr>
                        <td>Người phụ trách</td>
                        <td>{recipient_name}</td>
                    </tr>
                    <tr>
                        <td>Thời gian kiểm tra</td>
                        <td>{verification_time}</td>
                    </tr>
                    <tr>
                        <td>Tổng số trường bóc tách</td>
                        <td>{total_fields}</td>
                    </tr>
                    <tr>
                        <td>Trạng thái hồ sơ</td>
                        <td>{document_status}</td>
                    </tr>
                </table>

                <h3>Phân loại giấy tờ:</h3>
                <table>
                    <tr>
                        <th style="width: 50%;">Loại hồ sơ</th>
                        <th style="width: 35%;">Tài liệu thành phần</th>
                        <th style="width: 15%; text-align: center;">Số lượng</th>
                    </tr>
                    {categories_html}
                </table>

                <div class="footer">
                    <p>Bạn có thể vào liên kết sau để xem chi tiết và thực hiện các điều chỉnh cần thiết: <a href="{detail_url}">{detail_url}</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    return html_content


def _build_verified_lending_content(**kwargs):
    qttd_name = kwargs.get("recipient_name")
    qhkh_name = kwargs.get("qhkh_name")
    customer_name = kwargs.get("customer_name")
    document_type = kwargs.get("document_type")
    loan_purpose = kwargs.get("loan_purpose")
    loan_amount = kwargs.get("loan_amount")
    loan_term = kwargs.get("loan_term")
    verification_time = kwargs.get("verification_time")

    customer_info_result = kwargs.get("customer_info_result")
    all_keys = list(customer_info_result.keys())
    missing_keys = set(REQUIRED_EXTRACTION_FIELDS) - set(all_keys)
    none_keys = [key for key, value in customer_info_result.items() if value is None or value == ""]

    detail_url = kwargs.get("detail_url")

    content = f"""
    Kính gửi anh/chị {qttd_name}.
    Bộ hồ sơ vay vốn của {customer_name} đã được cán bộ QHKH {qhkh_name} xác minh thông qua hệ thống AgentDocCheck.
    Dưới đây là tóm tắt kết quả kiểm tra và đường dẫn truy cập hồ sơ:
    1. Thông tin hồ sơ:
       - Khách hàng: {customer_name}
       - Loại hồ sơ: {document_type}
       - Mục đích vay: {loan_purpose}
       - Số tiền đề nghị vay: {loan_amount}
       - Kỳ hạn vay: {loan_term}
       - Ngày kiểm tra: {verification_time}
       - Người phụ trách: {qhkh_name}
    2. Tóm tắt kết quả kiểm tra:
       - Hồ sơ đã được phân loại và bóc tách đầy đủ
       - Các trường thông tin bắt buộc đã được xác minh, ngoại trừ {none_keys + list(missing_keys)}
    Anh/chị vui lòng truy cập đường dẫn bên dưới để ra soát và hoàn thiện thông tin phân tích tín dụng.
    Link truy cập hồ sơ: {detail_url}"""
    return content


def send_lending_email(**kwargs):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = kwargs["recipient_email"]
    subject = "[RAWIQ] Tổng quan báo cáo của khách hàng xin vay vốn"
    body = build_lending_content(**kwargs)

    _send_email(sender_email, sender_password, recipient_email, subject, body)


def send_verified_lending_email(**kwargs):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    recipient_email = kwargs["recipient_email"]
    subject = "[RAWIQ] Tóm tắt bộ hồ sơ của khách hàng xin vay vốn"
    body = _build_verified_lending_content(**kwargs)

    _send_email(sender_email, sender_password, recipient_email, subject, body, "plain")


def _send_email(sender_email, sender_pw, recipient_email, subject, body, subtype="html"):
    if not isinstance(sender_email, str):
        sender_email = ", ".join(sender_email)
    if not isinstance(recipient_email, str):
        recipient_email = ", ".join(recipient_email)

    # msg = EmailMessage(policy=email.policy.SMTP)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    plain_payload = MIMEText("plain_body", 'plain')
    payload = MIMEText(body, subtype)
    msg.attach(plain_payload)
    msg.attach(payload)

    # Send email
    try:
        # For Gmail (change for other providers)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pw)

        server.send_message(msg)
        server.quit()
        print("✓ Validation email sent successfully!")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        return False
