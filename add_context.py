import pandas as pd


def add_faq_context():
    df = pd.read_csv(
        "C:\Temp\Tradera-Case\knowledge-base-export_Tradera - Vanliga frågor och svar_2023-04-04_091722.csv",
    )
    messages = [
        {
            "role": "user",
            "content": "Du är Traderas chatbot och kan endast svara på frågor rörande Tradera. Om svaret på frågan inte finns i chatthistoriken, referera till hemsidan https://info.tradera.com/",
        }
    ]

    for index, row in df.iterrows():
        messages.append({"role": "user", "content": row["title"]})
        messages.append({"role": "assistant", "content": row["content"]})

    return messages[:10]
