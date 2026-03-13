from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Boolean
from pathlib import Path
import json

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///livros.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Livro(db.Model):
    __tablename__ = "livros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    autor: Mapped[str] = mapped_column(String(120), nullable=False)
    idioma: Mapped[str] = mapped_column(String(10), nullable=False)
    editora: Mapped[str | None] = mapped_column(String(250))
    data_publicacao: Mapped[str | None] = mapped_column(String(10))
    descricao: Mapped[str | None] = mapped_column(Text)
    paginas: Mapped[int | None] = mapped_column(Integer)
    categorias: Mapped[str | None] = mapped_column(String(250))
    capinha_url: Mapped[str | None] = mapped_column(String(500))
    conteudo_maduro: Mapped[bool] = mapped_column(Boolean)
    isbn13: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)


with app.app_context():

    db.create_all()

    isbns_vistos = {
        isbn for (isbn,) in db.session.query(Livro.isbn13).all()
    }

    pasta = Path("./autores")
    livros = []

    for arquivo in pasta.glob("*.json"):

        with open(arquivo, encoding="utf-8") as f:
            data = json.load(f)

        for livro in data["items"]:

            info = livro["volumeInfo"]

            if info["language"] != "pt-BR" and "es" not in info["language"]:
                continue

            autores = info.get("authors", [])
            if not autores:
                continue

            editora = info.get("publisher", "")
            data_publicacao = info.get("publishedDate", "")
            descricao = info.get("description", "")
            paginas = info.get("pageCount")

            capinha = info.get("imageLinks", {}).get("thumbnail", "")

            flag_maduro = info.get("maturityRating", "")
            conteudo_maduro = False if flag_maduro in ["", "NOT_MATURE"] else True

            isbn13 = None

            if info.get("industryIdentifiers"):
                for isbn in info["industryIdentifiers"]:
                    if isbn["type"] == "ISBN_13":
                        isbn13 = isbn["identifier"]

            if not isbn13:
                continue

            if isbn13 in isbns_vistos:
                continue

            isbns_vistos.add(isbn13)

            novo_livro = Livro(
                titulo=info["title"],
                autor=autores[0] if len(autores) == 1 else "Vários autores",
                editora=editora,
                idioma=info["language"],
                data_publicacao=data_publicacao,
                descricao=descricao,
                paginas=paginas,
                categorias="",
                capinha_url=capinha,
                conteudo_maduro=conteudo_maduro,
                isbn13=isbn13,
            )

            livros.append(novo_livro)

    db.session.add_all(livros)
    db.session.commit()
