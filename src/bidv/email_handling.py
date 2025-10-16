import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
