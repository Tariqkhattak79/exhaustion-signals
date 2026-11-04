import requests

def send_signals_email(signals):
    if not signals:
        print("No signals found today. Email not sent.")
        return

    api_key = "re_AV4wGdqn_HRggH88HwN8QKguoHg5xRt5R"
    receiver = "soeffort1@gmail.com"

    signals.sort(key=lambda x: (x["category"] != "CAT A", -x["drop_pct"]))
    body = "EXHAUSTION SETUP SIGNALS FOR NEXT DAY\n\n"
    for s in signals:
        body += f"{s['symbol']} ({s['category']})\n"
        body += f"   Entry: Rs. {s['entry']} | Stop: Rs. {s['stop']} | Target: Rs. {s['target']}\n"
        body += f"   Drop: {s['drop_pct']}% over {s['drop_days']} days\n"
        body += f"   Vol: {s['today_vol']:,} vs {s['prev_vol']:,}\n"
        body += "-" * 40 + "\n"

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "PSX Alerts <onboarding@resend.dev>",
        "to": [receiver],
        "subject": f"{len(signals)} Exhaustion Signals Found",
        "text": body
    }

    print("Sending email via API...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Email sent successfully!")
        else:
            print(f"Failed to send: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
