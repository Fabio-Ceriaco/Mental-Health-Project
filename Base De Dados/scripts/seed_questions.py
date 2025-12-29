
from docx import Document
from sqlalchemy import create_engine
from APP.DATABASE.db_conn import Base, engine
from sqlalchemy.orm import sessionmaker
from APP.MODELS import Question
import re



DATABASE_URL = "sqlite:///./mental_health.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)



doc = Document("/Users/fabioceriaco/Mental_Health_Final/API/APP/perguntas.docx")



pattern = re.compile(r'[“"](.+?)[”"]\s*→\s*([0-9.]+)')

questions = []

for para in doc.paragraphs:
    text = para.text.strip()
    match = pattern.search(text)
    if match:
        q_text = match.group(1)
        weight = float(match.group(2))

    # Heurística para inverter perguntas positivas
        is_inverted = any(
            kw in q_text.lower()
            for kw in ["consigo", "sinto-me respeitado", "posso", "tenho tempo", "consigo desligar", "consigo lidar"]
        )

        # Dimensão aproximada por palavras-chave
        dim = "geral"
        if "stress" in q_text.lower() or "sobrecarregado" in q_text.lower() or "pressão" in q_text.lower():
            dim = "stress"
        elif "ansiedade" in q_text.lower() or "nervosismo" in q_text.lower() or "palpitações" in q_text.lower():
            dim = "ansiedade"
        elif "triste" in q_text.lower() or "desmotiv" in q_text.lower() or "perda de interesse" in q_text.lower():
            dim = "depressao"
        elif "esgot" in q_text.lower() or "burnout" in q_text.lower():
            dim = "burnout"
        elif "sono" in q_text.lower() or "dormir" in q_text.lower() or "adormecer" in q_text.lower():
            dim = "sono"
        elif "turno" in q_text.lower() or "horário" in q_text.lower():
            dim = "turnos"
        elif "dor" in q_text.lower() or "fadiga física" in q_text.lower() or "ergonom" in q_text.lower():
            dim = "ergonomia"

        questions.append((q_text, weight, dim, is_inverted))


db = SessionLocal()
for q_text, weight, dim, is_inverted in questions:
    q = Question(text=q_text, weight=weight, dimension=dim, is_inverted=is_inverted)
    db.add(q)

db.commit()
db.close()

print(f"{len(questions)} perguntas inseridas com sucesso.")
