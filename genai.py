import os
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from db import get_messages_from_db

load_dotenv()
ai_router = Router()

# Konfigurasi Gemini
genai.configure(api_key=os.getenv("GEN_API"))
model = genai.GenerativeModel("gemini-2.0-flash")


async def analyze_messages(days: int = 30) -> str:
    """
    Ambil pesan dari DB dan minta analisis ke model Gemini.
    """
    # Ambil pesan dari DB
    messages: List[str] = await get_messages_from_db()

    if not messages:
        return "Tidak ada pesan yang ditemukan untuk periode ini."

    # Gabungkan semua pesan menjadi satu teks
    text_data = "\n".join(m.strip() for m in messages if m and m.strip())

    prompt = f"""
Berikut adalah daftar pesan dari saluran Telegram saya beberapa waktu terakhir ({days} hari):
{text_data}

Berikan analisis singkat:
1. Apa tema yang paling umum?
2. Prestasi apa yang dapat disorot?
3. Berikan rekomendasi untuk bulan depan.
"""

    # Permintaan asinkron ke Gemini dengan penanganan error sederhana
    try:
        response = await model.generate_content_async(prompt)
        # Beberapa SDK menyediakan atribut berbeda; coba gunakan .text jika tersedia
        if hasattr(response, "text") and response.text:
            return response.text
        # Jika ada struktur kandidat (fallback)
        if hasattr(response, "candidates") and response.candidates:
            first = response.candidates[0]
            # beberapa implementasi menaruh teks di first.output[0].content[0].text atau serupa
            # di sini coba atribut umum
            return getattr(first, "text", str(first))
        # Jika tidak ada isi, kembalikan pesan default
        return "Model tidak mengembalikan analisis yang dapat dibaca."
    except Exception as e:
        # Log error bisa ditambahkan; untuk sekarang kembalikan pesan singkat
        return f"Gagal melakukan analisis: {e}"


@ai_router.message(Command("analyze"))
async def analyze_command(message: Message):
    await message.answer("🔍 Menganalisis pesan... Ini mungkin memakan waktu.")
    analysis = await analyze_messages(30)
    await message.answer(f"📊 Analisis selesai:\n\n{analysis}")
