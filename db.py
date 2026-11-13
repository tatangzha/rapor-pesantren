"""Database layer for E-Rapor Madrasah Islami Salafi Ihya 'Ulumiddin.
Supports Multi-Kelas (Kelas 1 - 6 MISIU), Multi-Wali Kelas, 63 Santri in Kelas 2,
Bulk Spreadsheet Input, Automatic Arab-Indo Conversions, Logo Customization, and Full SQLite Persistence.
"""

import json
import os
import random
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "rapor.db")

# Default 6 Classes Configuration
CLASSES_DATA = [
    {"id": "kls1", "nama": "Kelas 1 MISIU", "tingkat": 1, "wali_nama": "Ustadz Ahmad Fauzi", "wali_username": "wali1"},
    {"id": "kls2", "nama": "Kelas 2 MISIU", "tingkat": 2, "wali_nama": "TATANG", "wali_username": "tatang"},
    {"id": "kls3", "nama": "Kelas 3 MISIU", "tingkat": 3, "wali_nama": "Ustadz M. Ridwan", "wali_username": "wali3"},
    {"id": "kls4", "nama": "Kelas 4 MISIU", "tingkat": 4, "wali_nama": "Ustadzah Siti Fatimah", "wali_username": "wali4"},
    {"id": "kls5", "nama": "Kelas 5 MISIU", "tingkat": 5, "wali_nama": "Ustadz Abdul Halim", "wali_username": "wali5"},
    {"id": "kls6", "nama": "Kelas 6 MISIU", "tingkat": 6, "wali_nama": "Ustadz Hasan Basri", "wali_username": "wali6"},
]

# 44 Official Asatidz Pondok Pesantren Ihya 'Ulumiddin Tahun Pelajaran 2026/2027
ASATIDZ_DATA = [
    {"kode": 1, "nama": "Abah (KH. Amir Hamzah)", "username": "ust1", "alias": "abah"},
    {"kode": 2, "nama": "Ny. Momoh Maryamah", "username": "ust2", "alias": "momoh"},
    {"kode": 3, "nama": "Dr. KH. Ali Mahfudz, M.S.I.", "username": "ust3", "alias": "alimahfudz"},
    {"kode": 4, "nama": "Gus Muhamad Arsyad, S.Si.", "username": "ust4", "alias": "arsyad"},
    {"kode": 5, "nama": "Ny. Hj. Maya Sumayah S., M.Pd", "username": "ust5", "alias": "maya"},
    {"kode": 6, "nama": "Ustzh. Rufaidah Aslamiyah, M.A.", "username": "ust6", "alias": "rufaidah"},
    {"kode": 7, "nama": "Ust. Muhammad Ali Muhsin", "username": "ust7", "alias": "alimuhsin"},
    {"kode": 8, "nama": "Ust. Muslim", "username": "ust8", "alias": "muslim"},
    {"kode": 9, "nama": "Ust. Tobroni", "username": "ust9", "alias": "tobroni"},
    {"kode": 10, "nama": "Ust. Kholid Abdus Salam", "username": "ust10", "alias": "kholid"},
    {"kode": 11, "nama": "Ust. Mahasim", "username": "ust11", "alias": "mahasim"},
    {"kode": 12, "nama": "Ust. Sakirin", "username": "ust12", "alias": "sakirin"},
    {"kode": 13, "nama": "Ust. Nurcholik", "username": "ust13", "alias": "nurcholik"},
    {"kode": 14, "nama": "Ust. Misbahul Munir, S.Pd.", "username": "ust14", "alias": "misbahul"},
    {"kode": 15, "nama": "Ust. Dadan Tarsena, S.E.Sy.", "username": "ust15", "alias": "dadan"},
    {"kode": 16, "nama": "Ust. M. Ali Masykur, S.Kom.", "username": "ust16", "alias": "alimasykur"},
    {"kode": 17, "nama": "Ust. Juhdi Tamrin, A.Md.Kep.", "username": "ust17", "alias": "juhdi"},
    {"kode": 18, "nama": "Ust. Hadim A., S.Pd.I.", "username": "ust18", "alias": "hadim"},
    {"kode": 19, "nama": "Ust. Sarlan", "username": "ust19", "alias": "sarlan"},
    {"kode": 20, "nama": "Ust. Arif Pahmi Yazid. S.I.P.", "username": "ust20", "alias": "arif"},
    {"kode": 21, "nama": "Ust. Imar Abdurahman, S.Kom.", "username": "ust21", "alias": "imar"},
    {"kode": 22, "nama": "Ust. Taufik Hidayat, S.Pd.", "username": "ust22", "alias": "taufik"},
    {"kode": 23, "nama": "Ust. Yedi Hidayat", "username": "ust23", "alias": "yedi"},
    {"kode": 24, "nama": "Ust. Tatang", "username": "ust24", "alias": "tatang"},
    {"kode": 25, "nama": "Ust. Hilmi Ramdani", "username": "ust25", "alias": "hilmi"},
    {"kode": 26, "nama": "Ust. Ardi Herdiana, S.T.", "username": "ust26", "alias": "ardi"},
    {"kode": 27, "nama": "Ust. Sandi Saputra", "username": "ust27", "alias": "sandi"},
    {"kode": 28, "nama": "Ust. M. Ijad Nurzaman", "username": "ust28", "alias": "ijad"},
    {"kode": 29, "nama": "Ust. Irsad Al Mubarok", "username": "ust29", "alias": "irsad"},
    {"kode": 30, "nama": "Ust. M. Teguh Santoso", "username": "ust30", "alias": "teguh"},
    {"kode": 31, "nama": "Ust. M. Naqib Hakim", "username": "ust31", "alias": "naqib"},
    {"kode": 32, "nama": "Ust. Yusup Ibrahim", "username": "ust32", "alias": "yusup"},
    {"kode": 33, "nama": "Ustzh. Elwi Hayani", "username": "ust33", "alias": "elwi"},
    {"kode": 34, "nama": "Ustzh. Alis", "username": "ust34", "alias": "alis"},
    {"kode": 35, "nama": "Ustzh. Nurfarahim", "username": "ust35", "alias": "nurfarahim"},
    {"kode": 36, "nama": "Ustzh. Santi Pangestuti", "username": "ust36", "alias": "santi"},
    {"kode": 37, "nama": "Ustzh. Mutia Anggraeni", "username": "ust37", "alias": "mutia"},
    {"kode": 38, "nama": "Ustzh. Ranti Wildi Fauziah", "username": "ust38", "alias": "ranti"},
    {"kode": 39, "nama": "Ustzh. Sofi Hidayatul Qolbi", "username": "ust39", "alias": "sofi"},
    {"kode": 40, "nama": "Ustzh. Eva Pauziah", "username": "ust40", "alias": "eva"},
    {"kode": 41, "nama": "Ustzh. Susanti", "username": "ust41", "alias": "susanti"},
    {"kode": 42, "nama": "Ustzh. Rista Nurfadilah", "username": "ust42", "alias": "rista"},
    {"kode": 43, "nama": "Ustzh. Nilna Zadatun Ni'mah", "username": "ust43", "alias": "nilna"},
    {"kode": 44, "nama": "Ust. Husni Mubarok", "username": "ust44", "alias": "husni"},
]

ASATIDZ_BY_KODE = {a["kode"]: a for a in ASATIDZ_DATA}

# 39 Official Subject Codes (a - am) from Jadwal Pengajian 2026/2027
SUBJECT_CODES_MAP = {
    "a": {"indo": "Alfiyah Ibnu Aqil", "arab": "ألفية ابن عقيل"},
    "b": {"indo": "Al-Jurumiyah", "arab": "الجرمية"},
    "c": {"indo": "Al-Qur’an", "arab": "القرأن الكريم"},
    "d": {"indo": "Amtsilatu Tashrif", "arab": "امثلة التصريفية"},
    "e": {"indo": "Aqidatul Awam", "arab": "عقيدة العوام"},
    "f": {"indo": "Badul Amali", "arab": "بدء الأمالي"},
    "g": {"indo": "Faraidul Bahiyah", "arab": "الفرائد البهية"},
    "h": {"indo": "Fashalatan", "arab": "فصلة"},
    "i": {"indo": "Fathul Mu’in", "arab": "فتح المعين"},
    "j": {"indo": "Hidayatu Sibyan", "arab": "هداية الصبيان"},
    "k": {"indo": "Hidayatul Mustafid", "arab": "هداية المستفيد"},
    "l": {"indo": "Imrithi", "arab": "العمريطي"},
    "m": {"indo": "I'rob Al Muyassar", "arab": "الإعراب الميسر"},
    "n": {"indo": "Jauharu Tauhid", "arab": "جوهرة التوحيد"},
    "o": {"indo": "Jauharul Maknun", "arab": "الجوهر المكنون"},
    "p": {"indo": "Jazariyah", "arab": "الجزرية"},
    "q": {"indo": "Kaelani", "arab": "الكيلاني"},
    "r": {"indo": "Kharidatul Bahiyah", "arab": "الخريدة البهية"},
    "s": {"indo": "Khulashah Juz I", "arab": "خلاصة نور اليقين جزء ١"},
    "t": {"indo": "Khulashah Juz II", "arab": "خلاصة نور اليقين جزء ٢"},
    "u": {"indo": "Mabadiul Fiqih Juz I", "arab": "المبادئ الفقهية جزء ١"},
    "v": {"indo": "Maraqil Ubudiyyah", "arab": "مراقي العبودية"},
    "w": {"indo": "Murodan", "arab": "مراد"},
    "x": {"indo": "Nazham Maqsud", "arab": "نظم المقصود"},
    "y": {"indo": "Qawaidul I’lal", "arab": "قواعد الإعلال"},
    "z": {"indo": "Qira'atul Kutub (Safinah)", "arab": "قراءة الكتب (سفينة)"},
    "aa": {"indo": "Qiro'atul Kutub (Taqrib)", "arab": "قراءة الكتب (تقريب)"},
    "ab": {"indo": "Risalah Aswaja", "arab": "رسالة أهل السنة والجماعة"},
    "ac": {"indo": "Risalatul Mahidl", "arab": "رسالة المحيض"},
    "ad": {"indo": "Rohabiyah", "arab": "الرحبية"},
    "ae": {"indo": "Safinah", "arab": "سفينة النجا"},
    "af": {"indo": "Ta'limul Muta’alim", "arab": "تعليم المتعلم"},
    "ag": {"indo": "Tanbihul Muta’alim", "arab": "تنبيه المتعلمين"},
    "ah": {"indo": "Taqrib", "arab": "فتح القريب المجيب (تقريب)"},
    "ai": {"indo": "Tarikhul Hawadits", "arab": "تاريخ الحوادث"},
    "aj": {"indo": "Waroqot", "arab": "الورقات"},
    "ak": {"indo": "Washaya", "arab": "الوصايا"},
    "al": {"indo": "Yanbu’a", "arab": "ينبوعا"},
    "am": {"indo": "Sorogan", "arab": "سوروغان"},
}

# Official Signed Schedule Data (Jadwal Pengajian 2026/2027)
JADWAL_RESMI_DATA = {
    "title": "JADWAL PENGAJIAN PONDOK PESANTREN IHYA 'ULUMIDDIN",
    "tahunPelajaran": "TAHUN PELAJARAN 2026/2027",
    "pengesahan": {
        "tanggal": "Pamarican, 17 Juni 2026",
        "pengasuh": "KH. AMIR HAMZAH",
        "kepalaMadrasah": "TAUFIK HIDAYAT"
    },
    "days": [
        {
            "hari": "AHAD",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "16-ag", "kls2": "19-y", "kls3": "21-f", "kls4": "3-z", "kls5": "3-aa", "kls6": "3-aa"},
                {"waktu": "16.00 - 17.00", "kls1": "1-b", "kls2": "22-w", "kls3": "22-z", "kls4": "3-am", "kls5": "1-i", "kls6": "1-i"},
                {"waktu": "18.30 - 19.30", "kls1": "al*", "kls2": "c*", "kls3": "c*", "kls4": "3-c", "kls5": "3-c", "kls6": "3-c"},
                {"waktu": "20.00 - 21.00", "kls1": "18-e", "kls2": "33-ae", "kls3": "17-q", "kls4": "1-ad", "kls5": "1-ad", "kls6": "7-o"},
            ]
        },
        {
            "hari": "SENIN",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "b*", "kls2": "3-w", "kls3": "3-m", "kls4": "14-x", "kls5": "1-i", "kls6": "1-i"},
                {"waktu": "16.00 - 17.00", "kls1": "5-u", "kls2": "31-d", "kls3": "22-m", "kls4": "3-am", "kls5": "3-am", "kls6": "3-am"},
                {"waktu": "18.30 - 19.30", "kls1": "al*", "kls2": "c*", "kls3": "c*", "kls4": "3-c", "kls5": "3-c", "kls6": "3-c"},
                {"waktu": "20.00 - 21.00", "kls1": "34-d", "kls2": "13-k", "kls3": "5-af", "kls4": "44-n", "kls5": "1-a", "kls6": "1-a"},
            ]
        },
        {
            "hari": "SELASA",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "b*", "kls2": "31-d", "kls3": "3-m", "kls4": "14-x", "kls5": "1-i", "kls6": "1-i"},
                {"waktu": "16.00 - 17.00", "kls1": "34-d", "kls2": "22-w", "kls3": "12-p", "kls4": "3-z", "kls5": "3-am", "kls6": "3-am"},
                {"waktu": "18.30 - 19.30", "kls1": "al*", "kls2": "c*", "kls3": "c*", "kls4": "3-c", "kls5": "3-c", "kls6": "3-c"},
                {"waktu": "20.00 - 21.00", "kls1": "15-s", "kls2": "20-t", "kls3": "10-l", "kls4": "8-ah", "kls5": "1-a", "kls6": "1-a"},
            ]
        },
        {
            "hari": "RABU",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "34-d", "kls2": "3-w", "kls3": "3-m", "kls4": "9-aj", "kls5": "4-ai", "kls6": "1-v"},
                {"waktu": "16.00 - 17.00", "kls1": "6-ac", "kls2": "34-r", "kls3": "22-m", "kls4": "3-z", "kls5": "1-i", "kls6": "1-i"},
                {"waktu": "18.30 - 19.30", "kls1": "al*", "kls2": "c*", "kls3": "c*", "kls4": "3-c", "kls5": "3-c", "kls6": "3-c"},
                {"waktu": "20.00 - 21.00", "kls1": "11-j", "kls2": "39-ae", "kls3": "8-ah", "kls4": "1-ad", "kls5": "1-ad", "kls6": "4-ab"},
            ]
        },
        {
            "hari": "KAMIS",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "b*", "kls2": "31-d", "kls3": "3-m", "kls4": "9-aj", "kls5": "3-aa", "kls6": "3-aa"},
                {"waktu": "16.00 - 17.00", "kls1": "1-b", "kls2": "5-ak", "kls3": "22-z", "kls4": "3-am", "kls5": "3-am", "kls6": "3-am"},
                {"waktu": "18.30 - 19.30", "kls1": "PUTRA DAN PUTRI: HADROH & MARHABANAN", "kls2": "-", "kls3": "-", "kls4": "-", "kls5": "-", "kls6": "-"},
                {"waktu": "20.00 - 21.00", "kls1": "PUTRA DAN PUTRI: PENGAJIAN UMUM KITAB TAFSIR JALALAIN", "kls2": "-", "kls3": "-", "kls4": "-", "kls5": "-", "kls6": "-"},
            ]
        },
        {
            "hari": "JUM'AT",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "PUTRA: ZIARAH KUBUR | PUTRI: PEMBACAAN SURAT AL-KAHFI, YASIN & WAQI'AH", "kls2": "-", "kls3": "-", "kls4": "-", "kls5": "-", "kls6": "-"},
                {"waktu": "16.00 - 17.00", "kls1": "h*", "kls2": "22-w", "kls3": "17-q", "kls4": "3-am", "kls5": "1-i", "kls6": "1-i"},
                {"waktu": "18.30 - 19.30", "kls1": "al*", "kls2": "c*", "kls3": "c*", "kls4": "3-c", "kls5": "3-c", "kls6": "3-c"},
                {"waktu": "20.00 - 21.00", "kls1": "h*", "kls2": "13-k", "kls3": "8-ah", "kls4": "44-n", "kls5": "1-a", "kls6": "1-a"},
            ]
        },
        {
            "hari": "SABTU",
            "slots": [
                {"waktu": "05.00 - 06.00", "kls1": "b*", "kls2": "19-y", "kls3": "21-f", "kls4": "3-z", "kls5": "3-aa", "kls6": "3-aa"},
                {"waktu": "16.00 - 17.00", "kls1": "34-d", "kls2": "34-r", "kls3": "22-z", "kls4": "3-am", "kls5": "3-am", "kls6": "3-am"},
                {"waktu": "18.30 - 19.30", "kls1": "PUTRA: SHOLAWAT AL-BARZANJI | PUTRI: NADZOMAN", "kls2": "-", "kls3": "-", "kls4": "-", "kls5": "-", "kls6": "-"},
                {"waktu": "20.00 - 21.00", "kls1": "34-d", "kls2": "33-ae", "kls3": "10-l", "kls4": "8-ah", "kls5": "7-g", "kls6": "7-o"},
            ]
        },
    ],
    "keterangan": [
        {"kode": "al* / c*", "mapel": "Yanbu'a (Kelas 1) & Al-Qur'an (Kelas 2–3)", "putra": [3, 24, 25, 23, 27, 30, 31, 32], "putri": [2, 35, 36, 37, 39, 42, 43]},
        {"kode": "b*", "mapel": "Al-Jurumiyah (Kelas 1)", "umum": [1], "putra": [26, 29], "putri": [33, 37, 38]},
        {"kode": "h*", "mapel": "Fashalatan (Kelas 1)", "putra": [28, 30], "putri": [40, 41]},
    ],
    "rutinan": [
        "1. BA'DA MAGHRIB: Qiro'atul Qur'an & Yanbu'a",
        "2. BA'DA SUBUH: Muhafadhoh (Hafalan)",
        "3. BA'DA ASHAR: Sorogan / Pengajian Kitab",
        "4. BA'DA ISYA: Pengajian Kitab Kuning (Takhasus / Klasikal)"
    ],
    "tempatPengajian": [
        {"kelas": "Kelas 1 MISIU", "tempat": "Asrama Putra / Kobong & Mushola"},
        {"kelas": "Kelas 2 MISIU", "tempat": "Madrasah Lt. 1"},
        {"kelas": "Kelas 3 MISIU", "tempat": "Madrasah Lt. 2"},
        {"kelas": "Kelas 4 MISIU", "tempat": "Masjid Pondok"},
        {"kelas": "Kelas 5 MISIU", "tempat": "Majelis Utama"},
        {"kelas": "Kelas 6 MISIU", "tempat": "Ndalem / Aula Pengasuh"},
    ]
}

# Official 2026/2027 Curriculum per Class synchronized with Signed Schedule
CURRICULUM_BY_CLASS = {
    "kls1": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "ag", "indo": "Tanbihul Muta’alim", "arab": "تنبيه المتعلمين", "active": True},
            {"id": "t2", "no": 2, "code": "b", "indo": "Al-Jurumiyah", "arab": "الجرمية", "active": True},
            {"id": "t3", "no": 3, "code": "d", "indo": "Amtsilatu Tashrif", "arab": "امثلة التصريفية", "active": True},
            {"id": "t4", "no": 4, "code": "e", "indo": "Aqidatul Awam", "arab": "عقيدة العوام", "active": True},
            {"id": "t5", "no": 5, "code": "u", "indo": "Mabadiul Fiqih Juz I", "arab": "المبادئ الفقهية جزء ١", "active": True},
            {"id": "t6", "no": 6, "code": "s", "indo": "Khulashah Juz I", "arab": "خلاصة نور اليقين جزء ١", "active": True},
            {"id": "t7", "no": 7, "code": "ac", "indo": "Risalatul Mahidl", "arab": "رسالة المحيض", "active": True},
            {"id": "t8", "no": 8, "code": "j", "indo": "Hidayatu Sibyan", "arab": "هداية الصبيان", "active": True},
            {"id": "t9", "no": 9, "code": "h", "indo": "Fashalatan", "arab": "فصلة", "active": True},
            {"id": "t10", "no": 10, "code": "al", "indo": "Yanbu’a", "arab": "ينبوعا", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "al", "indo": "Yanbu’a", "arab": "ينبوعا", "active": True},
            {"id": "h2", "no": 2, "code": "", "indo": "Doa Harian & Hadits", "arab": "الأدعية والحديث", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "b", "indo": "Al-Jurumiyah", "arab": "الجرمية", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    },
    "kls2": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "y", "indo": "Qawaidul I’lal", "arab": "قواعد الإعلال", "active": True},
            {"id": "t2", "no": 2, "code": "w", "indo": "Murodan", "arab": "مراد", "active": True},
            {"id": "t3", "no": 3, "code": "d", "indo": "Amtsilatu Tashrif", "arab": "امثلة التصريفية", "active": True},
            {"id": "t4", "no": 4, "code": "ae", "indo": "Safinah", "arab": "سفينة النجا", "active": True},
            {"id": "t5", "no": 5, "code": "r", "indo": "Kharidatul Bahiyah", "arab": "الخريدة البهية", "active": True},
            {"id": "t6", "no": 6, "code": "k", "indo": "Hidayatul Mustafid", "arab": "هداية المستفيد", "active": True},
            {"id": "t7", "no": 7, "code": "t", "indo": "Khulashah Juz II", "arab": "خلاصة نور اليقين جزء ٢", "active": True},
            {"id": "t8", "no": 8, "code": "ak", "indo": "Washaya", "arab": "الوصايا", "active": True},
            {"id": "t9", "no": 9, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "t10", "no": 10, "code": "", "indo": "Mapel Tulis 10", "arab": "الكتابة ١٠", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن", "active": True},
            {"id": "h2", "no": 2, "code": "", "indo": "Hafalan Tambahan", "arab": "المحافظة الإضافية", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "ae", "indo": "Safinah", "arab": "سفينة النجا", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    },
    "kls3": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "f", "indo": "Badul Amali", "arab": "بدء الأمالي", "active": True},
            {"id": "t2", "no": 2, "code": "m", "indo": "I'rob Al Muyassar", "arab": "الإعراب الميسر", "active": True},
            {"id": "t3", "no": 3, "code": "z", "indo": "Qira'atul Kutub (Safinah)", "arab": "قراءة الكتب (سفينة)", "active": True},
            {"id": "t4", "no": 4, "code": "p", "indo": "Jazariyah", "arab": "الجزرية", "active": True},
            {"id": "t5", "no": 5, "code": "q", "indo": "Kaelani", "arab": "الكيلاني", "active": True},
            {"id": "t6", "no": 6, "code": "af", "indo": "Ta'limul Muta’alim", "arab": "تعليم المتعلم", "active": True},
            {"id": "t7", "no": 7, "code": "l", "indo": "Imrithi", "arab": "العمريطي", "active": True},
            {"id": "t8", "no": 8, "code": "ah", "indo": "Taqrib", "arab": "فتح القريب المجيب (تقريب)", "active": True},
            {"id": "t9", "no": 9, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "t10", "no": 10, "code": "", "indo": "Mapel Tulis 10", "arab": "الكتابة ١٠", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن", "active": True},
            {"id": "h2", "no": 2, "code": "l", "indo": "Nadhom Imrithi", "arab": "نظم العمريطي", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "z", "indo": "Qira'atul Kutub (Safinah)", "arab": "قراءة الكتب (سفينة)", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    },
    "kls4": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "z", "indo": "Qira'atul Kutub (Safinah)", "arab": "قراءة الكتب (سفينة)", "active": True},
            {"id": "t2", "no": 2, "code": "x", "indo": "Nazham Maqsud", "arab": "نظم المقصود", "active": True},
            {"id": "t3", "no": 3, "code": "am", "indo": "Sorogan", "arab": "سوروغان", "active": True},
            {"id": "t4", "no": 4, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "t5", "no": 5, "code": "ad", "indo": "Rohabiyah", "arab": "الرحبية", "active": True},
            {"id": "t6", "no": 6, "code": "n", "indo": "Jauharu Tauhid", "arab": "جوهرة التوحيد", "active": True},
            {"id": "t7", "no": 7, "code": "ah", "indo": "Taqrib", "arab": "فتح القريب المجيب (تقريب)", "active": True},
            {"id": "t8", "no": 8, "code": "aj", "indo": "Waroqot", "arab": "الورقات", "active": True},
            {"id": "t9", "no": 9, "code": "", "indo": "Mapel Tulis 9", "arab": "الكتابة ٩", "active": False},
            {"id": "t10", "no": 10, "code": "", "indo": "Mapel Tulis 10", "arab": "الكتابة ١٠", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "h2", "no": 2, "code": "x", "indo": "Nazham Maqsud", "arab": "نظم المقصود", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "z", "indo": "Qira'atul Kutub (Safinah)", "arab": "قراءة الكتب (سفينة)", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    },
    "kls5": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "aa", "indo": "Qiro'atul Kutub (Taqrib)", "arab": "قراءة الكتب (تقريب)", "active": True},
            {"id": "t2", "no": 2, "code": "i", "indo": "Fathul Mu’in", "arab": "فتح المعين", "active": True},
            {"id": "t3", "no": 3, "code": "am", "indo": "Sorogan", "arab": "سوروغان", "active": True},
            {"id": "t4", "no": 4, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "t5", "no": 5, "code": "ad", "indo": "Rohabiyah", "arab": "الرحبية", "active": True},
            {"id": "t6", "no": 6, "code": "a", "indo": "Alfiyah Ibnu Aqil", "arab": "ألفية ابن عقيل", "active": True},
            {"id": "t7", "no": 7, "code": "ai", "indo": "Tarikhul Hawadits", "arab": "تاريخ الحوادث", "active": True},
            {"id": "t8", "no": 8, "code": "g", "indo": "Faraidul Bahiyah", "arab": "الفرائد البهية", "active": True},
            {"id": "t9", "no": 9, "code": "", "indo": "Mapel Tulis 9", "arab": "الكتابة ٩", "active": False},
            {"id": "t10", "no": 10, "code": "", "indo": "Mapel Tulis 10", "arab": "الكتابة ١٠", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "a", "indo": "Alfiyah Ibnu Aqil", "arab": "ألفية ابن عقيل", "active": True},
            {"id": "h2", "no": 2, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "aa", "indo": "Qiro'atul Kutub (Taqrib)", "arab": "قراءة الكتب (تقريب)", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    },
    "kls6": {
        "tulis": [
            {"id": "t1", "no": 1, "code": "aa", "indo": "Qiro'atul Kutub (Taqrib)", "arab": "قراءة الكتب (تقريب)", "active": True},
            {"id": "t2", "no": 2, "code": "i", "indo": "Fathul Mu’in", "arab": "فتح المعين", "active": True},
            {"id": "t3", "no": 3, "code": "am", "indo": "Sorogan", "arab": "سوروغان", "active": True},
            {"id": "t4", "no": 4, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": True},
            {"id": "t5", "no": 5, "code": "o", "indo": "Jauharul Maknun", "arab": "الجوهر المكنون", "active": True},
            {"id": "t6", "no": 6, "code": "a", "indo": "Alfiyah Ibnu Aqil", "arab": "ألفية ابن عقيل", "active": True},
            {"id": "t7", "no": 7, "code": "v", "indo": "Maraqil Ubudiyyah", "arab": "مراقي العبودية", "active": True},
            {"id": "t8", "no": 8, "code": "ab", "indo": "Risalah Aswaja", "arab": "رسالة أهل السنة والجماعة", "active": True},
            {"id": "t9", "no": 9, "code": "", "indo": "Mapel Tulis 9", "arab": "الكتابة ٩", "active": False},
            {"id": "t10", "no": 10, "code": "", "indo": "Mapel Tulis 10", "arab": "الكتابة ١٠", "active": False},
            {"id": "t11", "no": 11, "code": "", "indo": "Mapel Tulis 11", "arab": "الكتابة ١١", "active": False},
            {"id": "t12", "no": 12, "code": "", "indo": "Mapel Tulis 12", "arab": "الكتابة ١٢", "active": False}
        ],
        "hafalan": [
            {"id": "h1", "no": 1, "code": "a", "indo": "Alfiyah Ibnu Aqil", "arab": "ألفية ابن عقيل", "active": True},
            {"id": "h2", "no": 2, "code": "c", "indo": "Al-Qur’an", "arab": "القرأن الكريم", "active": False}
        ],
        "kitab": [
            {"id": "k1", "no": 1, "code": "aa", "indo": "Qiro'atul Kutub (Taqrib)", "arab": "قراءة الكتب (تقريب)", "active": True},
            {"id": "k2", "no": 2, "code": "", "indo": "Kitab Tambahan", "arab": "الكتاب الإضافي", "active": False}
        ]
    }
}

DEFAULT_SUBJECTS = CURRICULUM_BY_CLASS["kls2"]


def get_class_curriculum_template(class_id):
    return CURRICULUM_BY_CLASS.get(class_id, CURRICULUM_BY_CLASS["kls2"])


def build_official_teacher_assignments():
    """Build exact teacher assignments for all 44 Asatidz across Kelas 1 - 6 MISIU based on Jadwal Pengajian 2026/2027."""
    tim_yanbua_quran_putra = [(k, "L") for k in [3, 24, 25, 23, 27, 30, 31, 32]]
    tim_yanbua_quran_putri = [(k, "P") for k in [2, 35, 36, 37, 39, 42, 43]]
    tim_yanbua_quran = tim_yanbua_quran_putra + tim_yanbua_quran_putri

    tim_jurumiyah_kls1 = [(1, "ALL"), (26, "L"), (29, "L"), (33, "P"), (37, "P"), (38, "P")]
    tim_fashalatan_kls1 = [(28, "L"), (30, "L"), (40, "P"), (41, "P")]

    raw_map = {
        "kls1": [
            ("tulis", 0, "ag", "Tanbihul Muta’alim", [(16, "ALL")]),
            ("tulis", 1, "b", "Al-Jurumiyah", tim_jurumiyah_kls1),
            ("tulis", 2, "d", "Amtsilatu Tashrif", [(34, "ALL")]),
            ("tulis", 3, "e", "Aqidatul Awam", [(18, "ALL")]),
            ("tulis", 4, "u", "Mabadiul Fiqih Juz I", [(5, "ALL")]),
            ("tulis", 5, "s", "Khulashah Juz I", [(15, "ALL")]),
            ("tulis", 6, "ac", "Risalatul Mahidl", [(6, "ALL")]),
            ("tulis", 7, "j", "Hidayatu Sibyan", [(11, "ALL")]),
            ("tulis", 8, "h", "Fashalatan", tim_fashalatan_kls1),
            ("hafalan", 0, "al", "Yanbu’a (Hafalan/Membaca)", tim_yanbua_quran),
            ("kitab", 0, "b", "Al-Jurumiyah (Tes Baca Kitab)", tim_jurumiyah_kls1),
        ],
        "kls2": [
            ("tulis", 0, "y", "Qawaidul I’lal", [(19, "ALL")]),
            ("tulis", 1, "w", "Murodan", [(22, "ALL"), (3, "ALL")]),
            ("tulis", 2, "d", "Amtsilatu Tashrif", [(31, "ALL")]),
            ("tulis", 3, "ae", "Safinah", [(33, "ALL"), (39, "ALL")]),
            ("tulis", 4, "r", "Kharidatul Bahiyah", [(34, "ALL")]),
            ("tulis", 5, "k", "Hidayatul Mustafid", [(13, "ALL")]),
            ("tulis", 6, "t", "Khulashah Juz II", [(20, "ALL")]),
            ("tulis", 7, "ak", "Washaya", [(5, "ALL")]),
            ("tulis", 8, "c", "Al-Qur’an", tim_yanbua_quran),
            ("hafalan", 0, "c", "Al-Qur’an (Hafalan/Membaca)", tim_yanbua_quran),
            ("kitab", 0, "ae", "Safinah (Tes Baca Kitab)", [(33, "ALL"), (39, "ALL")]),
        ],
        "kls3": [
            ("tulis", 0, "f", "Badul Amali", [(21, "ALL")]),
            ("tulis", 1, "m", "I'rob Al Muyassar", [(3, "ALL"), (22, "ALL")]),
            ("tulis", 2, "z", "Qira'atul Kutub (Safinah)", [(22, "ALL")]),
            ("tulis", 3, "p", "Jazariyah", [(12, "ALL")]),
            ("tulis", 4, "q", "Kaelani", [(17, "ALL")]),
            ("tulis", 5, "af", "Ta'limul Muta’alim", [(5, "ALL")]),
            ("tulis", 6, "l", "Imrithi", [(10, "ALL")]),
            ("tulis", 7, "ah", "Taqrib", [(8, "ALL")]),
            ("tulis", 8, "c", "Al-Qur’an", tim_yanbua_quran),
            ("hafalan", 0, "c", "Al-Qur’an (Hafalan/Membaca)", tim_yanbua_quran),
            ("kitab", 0, "z", "Qira'atul Kutub (Safinah) (Tes Baca Kitab)", [(22, "ALL")]),
        ],
        "kls4": [
            ("tulis", 0, "z", "Qira'atul Kutub (Safinah)", [(3, "ALL")]),
            ("tulis", 1, "x", "Nazham Maqsud", [(14, "ALL")]),
            ("tulis", 2, "am", "Sorogan", [(3, "ALL")]),
            ("tulis", 3, "c", "Al-Qur’an", [(3, "ALL")]),
            ("tulis", 4, "ad", "Rohabiyah", [(1, "ALL")]),
            ("tulis", 5, "n", "Jauharu Tauhid", [(44, "ALL")]),
            ("tulis", 6, "ah", "Taqrib", [(8, "ALL")]),
            ("tulis", 7, "aj", "Waroqot", [(9, "ALL")]),
            ("hafalan", 0, "c", "Al-Qur’an (Hafalan/Membaca)", [(3, "ALL")]),
            ("kitab", 0, "z", "Qira'atul Kutub (Safinah) (Tes Baca Kitab)", [(3, "ALL")]),
        ],
        "kls5": [
            ("tulis", 0, "aa", "Qiro'atul Kutub (Taqrib)", [(3, "ALL")]),
            ("tulis", 1, "i", "Fathul Mu’in", [(1, "ALL")]),
            ("tulis", 2, "am", "Sorogan", [(3, "ALL")]),
            ("tulis", 3, "c", "Al-Qur’an", [(3, "ALL")]),
            ("tulis", 4, "ad", "Rohabiyah", [(1, "ALL")]),
            ("tulis", 5, "a", "Alfiyah Ibnu Aqil", [(1, "ALL")]),
            ("tulis", 6, "ai", "Tarikhul Hawadits", [(4, "ALL")]),
            ("tulis", 7, "g", "Faraidul Bahiyah", [(7, "ALL")]),
            ("hafalan", 0, "a", "Alfiyah Ibnu Aqil (Hafalan Nadhom)", [(1, "ALL")]),
            ("kitab", 0, "aa", "Qiro'atul Kutub (Taqrib) (Tes Baca Kitab)", [(3, "ALL")]),
        ],
        "kls6": [
            ("tulis", 0, "aa", "Qiro'atul Kutub (Taqrib)", [(3, "ALL")]),
            ("tulis", 1, "i", "Fathul Mu’in", [(1, "ALL")]),
            ("tulis", 2, "am", "Sorogan", [(3, "ALL")]),
            ("tulis", 3, "c", "Al-Qur’an", [(3, "ALL")]),
            ("tulis", 4, "o", "Jauharul Maknun", [(7, "ALL")]),
            ("tulis", 5, "a", "Alfiyah Ibnu Aqil", [(1, "ALL")]),
            ("tulis", 6, "v", "Maraqil Ubudiyyah", [(1, "ALL")]),
            ("tulis", 7, "ab", "Risalah Aswaja", [(4, "ALL")]),
            ("hafalan", 0, "a", "Alfiyah Ibnu Aqil (Hafalan Nadhom)", [(1, "ALL")]),
            ("kitab", 0, "aa", "Qiro'atul Kutub (Taqrib) (Tes Baca Kitab)", [(3, "ALL")]),
        ],
    }

    assignments = []
    for cid, items in raw_map.items():
        for cat, idx, scode, sname, teachers in items:
            s_arab = SUBJECT_CODES_MAP.get(scode, {}).get("arab", "")
            for kode, jk_filter in teachers:
                assignments.append({
                    "asatidz_kode": kode,
                    "class_id": cid,
                    "subject_category": cat,
                    "subject_index": idx,
                    "subject_code": scode,
                    "subject_name": sname,
                    "subject_arab": s_arab,
                    "jk_filter": jk_filter,
                })
    return assignments


# The official 63 students for Kelas 2 MISIU with grades initialized to 0
STUDENTS_KLS2 = [
    {"nis": "2526010286", "nama": "ABABIL ULUL ALBAB", "jk": "L", "wali": "HENDI LALA"},
    {"nis": "2526010287", "nama": "ADIT KURNIAWAN", "jk": "L", "wali": "CUCU SAMSUDIN"},
    {"nis": "2526010288", "nama": "AFIFAH NUR FADILAH", "jk": "P", "wali": "-"},
    {"nis": "2526010289", "nama": "AI 'AFIFAH SRI ZAKIYAH", "jk": "P", "wali": "JAENUDIN"},
    {"nis": "2526010290", "nama": "AKHTAR ILHAM", "jk": "L", "wali": "WAHIDIN"},
    {"nis": "2526010291", "nama": "ALFIN HIDAYATULLOH", "jk": "L", "wali": "AJO SUJANA"},
    {"nis": "2425010230", "nama": "ALFIZ ZAFIRA", "jk": "P", "wali": "MUHAMAD YASIN"},
    {"nis": "2526010292", "nama": "ALWI NURDZIKRI FATAHILAH", "jk": "L", "wali": "TURASNO"},
    {"nis": "2526010293", "nama": "ALYA ANGGRAENI", "jk": "P", "wali": "MUMU MUTAKIN"},
    {"nis": "2526010294", "nama": "ANGGUN QISTINA MUFIDAH", "jk": "P", "wali": "ATENG SURYANA"},
    {"nis": "2526010295", "nama": "ARIEF RACHMAN KHAKIM", "jk": "L", "wali": "-"},
    {"nis": "2526010296", "nama": "AYUSUP", "jk": "L", "wali": "DEDE USMAN"},
    {"nis": "2526010297", "nama": "AZIS KUSMAWAN", "jk": "L", "wali": "-"},
    {"nis": "2425010285", "nama": "DAFFA KHAIRUL IKHWAN", "jk": "L", "wali": "-"},
    {"nis": "2526010298", "nama": "DEDE FARID HAMZAH", "jk": "L", "wali": "USUP SUPRIADI"},
    {"nis": "2526010299", "nama": "DEWI LESTARI", "jk": "P", "wali": "JANA"},
    {"nis": "2526010300", "nama": "DIAN AYU TRI ASTUTI", "jk": "P", "wali": "HADI SONO"},
    {"nis": "2526010301", "nama": "DIANDRA AQILA PUTRI", "jk": "P", "wali": "ARI GUSTIANI"},
    {"nis": "2526010302", "nama": "FAKHRI DAFFA RAMADHAN", "jk": "L", "wali": "HANIPUDIN"},
    {"nis": "2526010303", "nama": "FATWATUL LESTARI", "jk": "P", "wali": "M PARTIMAN S"},
    {"nis": "2526010304", "nama": "FITRI ALYA JULIANTI", "jk": "P", "wali": "SARIPIN"},
    {"nis": "2526010305", "nama": "GHANI IJMA ALFARISI", "jk": "L", "wali": "IJANG"},
    {"nis": "2526010306", "nama": "GILANG RAMADHAN MAULANA", "jk": "L", "wali": "EMAN"},
    {"nis": "2526010307", "nama": "HAMZAH FANSHURI", "jk": "L", "wali": "LASIMAN"},
    {"nis": "2526010308", "nama": "HANAA LISMUFIIDAH", "jk": "P", "wali": "SURYADI"},
    {"nis": "2526010309", "nama": "IBNI FAIRUZ", "jk": "L", "wali": "DAYAT"},
    {"nis": "2526010310", "nama": "INDRA FARID AZAHIR", "jk": "L", "wali": "ROSMAWATI"},
    {"nis": "2526010311", "nama": "INDRA KUSWANTO", "jk": "L", "wali": "AGUS KUSWANTO"},
    {"nis": "2526010312", "nama": "IRSYAD NABAWI", "jk": "L", "wali": "AJAT SUDRAJAT"},
    {"nis": "2526010314", "nama": "LISKA NOVITA SAFITRI", "jk": "P", "wali": "MASNAN"},
    {"nis": "2526010315", "nama": "MIZAN ARIFIN AL ASHRAFI", "jk": "L", "wali": "M ARIFIN"},
    {"nis": "2526010316", "nama": "MOCHAMAD ANDRA APRIANA", "jk": "L", "wali": "AAN NURHIDAYAT"},
    {"nis": "2526010318", "nama": "MUHAMMAD AZKA ILJAM ATALLAH", "jk": "L", "wali": "SAMSUL MA'ARIF"},
    {"nis": "2526010319", "nama": "MUHAMMAD HILMI MUFAROZ", "jk": "L", "wali": "ABDUL BASITH"},
    {"nis": "2526010320", "nama": "MUTIARA SAFITRI", "jk": "P", "wali": "LASNO"},
    {"nis": "2526010321", "nama": "NABILA SUKMA N. M.", "jk": "P", "wali": "-"},
    {"nis": "2526010322", "nama": "NADIA NURFADILAH", "jk": "P", "wali": "RASNO"},
    {"nis": "2526010323", "nama": "NADZIFA ZULFA AQILA", "jk": "P", "wali": "TAUFIQ ARIFIN"},
    {"nis": "2526010324", "nama": "NASYA KALILA RASYA PUTRI", "jk": "P", "wali": "-"},
    {"nis": "2526010325", "nama": "NASYWAA NURUL HIDAYAH", "jk": "P", "wali": "AJIS KUSNENDI"},
    {"nis": "2526010326", "nama": "NATASYA FITRI NURUL AISYAH", "jk": "P", "wali": "HUSRON"},
    {"nis": "2526010327", "nama": "NAYA AZWA KURNIA SENJAYA", "jk": "P", "wali": "DENA KURNIA S"},
    {"nis": "2526010328", "nama": "NAZWA AZIYA FADILAH", "jk": "L", "wali": "RIDWAN FADILAH"},
    {"nis": "2526010329", "nama": "NUROTUN NABILAH", "jk": "P", "wali": "JABIDI"},
    {"nis": "2526010330", "nama": "PRICILA AGNIA AKMAL", "jk": "P", "wali": "ENDANG KUSMAYA"},
    {"nis": "2526010331", "nama": "QONITA AISYA SYAFIQO", "jk": "P", "wali": "AHMAD FAIZAL"},
    {"nis": "2526010332", "nama": "RAFI SEPTA NUGRAHA", "jk": "L", "wali": "IWAN"},
    {"nis": "2526010334", "nama": "RAHMA DINA N. F.", "jk": "P", "wali": "-"},
    {"nis": "2526010335", "nama": "RAIHANATUZZAHRO", "jk": "P", "wali": "NURUL HUDA"},
    {"nis": "2526010336", "nama": "RAIHATUL JANNAH", "jk": "P", "wali": "-"},
    {"nis": "2526010337", "nama": "RAYHAN FARID WAHYUDIN", "jk": "L", "wali": "WAHYUDIN"},
    {"nis": "2526010338", "nama": "RIZAL FARHIN", "jk": "L", "wali": "SUDARYA"},
    {"nis": "2526010339", "nama": "RIZKI FAHMI FIRMANSYAH", "jk": "L", "wali": "WENI"},
    {"nis": "2526010340", "nama": "RIZKI ISKANDAR", "jk": "L", "wali": "HARJO"},
    {"nis": "2526010341", "nama": "RIZKI NAUFAL GHANI", "jk": "L", "wali": "HENDRI"},
    {"nis": "2526010342", "nama": "RIZQI AMALIYADI", "jk": "L", "wali": "SUGENG PRIYANTO"},
    {"nis": "2425010284", "nama": "SHERIN APRILIA", "jk": "P", "wali": "YAYAN"},
    {"nis": "2526010343", "nama": "SIFA OKTAVIANI", "jk": "P", "wali": "-"},
    {"nis": "2526010344", "nama": "SUBHAN FAWWAZ", "jk": "L", "wali": "ROHMAN TULOH"},
    {"nis": "2526010345", "nama": "VANILA CAHYA KAMILA", "jk": "P", "wali": "DEDI WISWANTO"},
    {"nis": "2526010346", "nama": "ZAINAL ARIFIN RAMADANI", "jk": "L", "wali": "ABDUL MUNIB"},
    {"nis": "2526010347", "nama": "ZIDAN AKMAL MUSYAFA", "jk": "L", "wali": "SUDARSONO"},
    {"nis": "2526010348", "nama": "ZIDNI HUDA MUBAROK", "jk": "L", "wali": "BASIR NURDIN"}
]

SAMPLE_STUDENTS_OTHER = {
    "kls1": [
        {"nis": "2627010001", "nama": "AHMAD ZAKI MUBAROK", "jk": "L", "wali": "MUBAROK"},
        {"nis": "2627010002", "nama": "BILQIS HUMAIRA", "jk": "P", "wali": "SUHENDRA"},
        {"nis": "2627010003", "nama": "DZAKY AL-FARISI", "jk": "L", "wali": "FARIS"},
    ],
    "kls3": [
        {"nis": "2425010001", "nama": "BAGAS PRASETYO", "jk": "L", "wali": "PRASETYO"},
        {"nis": "2425010002", "nama": "CANTIKA PUTRI", "jk": "P", "wali": "HERI"},
    ],
    "kls4": [
        {"nis": "2324010001", "nama": "DANI RAMDHANI", "jk": "L", "wali": "RAMDHAN"},
    ],
    "kls5": [
        {"nis": "2223010001", "nama": "FAISAL MAJID", "jk": "L", "wali": "MAJID"},
    ],
    "kls6": [
        {"nis": "2122010001", "nama": "HABIBIE ROZAK", "jk": "L", "wali": "ROZAK"},
    ],
}


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _create_tables(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        val TEXT
    );

    CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY,
        nama TEXT NOT NULL,
        tingkat INTEGER NOT NULL,
        wali_nama TEXT NOT NULL,
        wali_username TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS class_semester_config (
        class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        sem_key TEXT NOT NULL,
        label TEXT NOT NULL,
        kelas_title TEXT NOT NULL,
        tahun_pelajaran TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        wali_kelas TEXT NOT NULL,
        kepala_madrasah TEXT NOT NULL,
        arab_header_col TEXT NOT NULL,
        sec_b_indo TEXT NOT NULL,
        sec_b_arab TEXT NOT NULL,
        sec_c_indo TEXT NOT NULL,
        sec_c_arab TEXT NOT NULL,
        show_keputusan INTEGER NOT NULL DEFAULT 0,
        subjects_json TEXT NOT NULL,
        PRIMARY KEY (class_id, sem_key)
    );

    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        nis TEXT UNIQUE NOT NULL,
        nama TEXT NOT NULL,
        jk TEXT DEFAULT 'L',
        wali TEXT DEFAULT '',
        ttl TEXT DEFAULT '',
        agama TEXT DEFAULT 'Islam',
        anak_ke TEXT DEFAULT '',
        status_keluarga TEXT DEFAULT 'Anak Kandung',
        alamat TEXT DEFAULT '',
        diterima_kelas TEXT DEFAULT '',
        diterima_tanggal TEXT DEFAULT '',
        sekolah_asal TEXT DEFAULT '',
        sekolah_asal_alamat TEXT DEFAULT '',
        ayah_nama TEXT DEFAULT '',
        ibu_nama TEXT DEFAULT '',
        ortu_alamat TEXT DEFAULT '',
        no_hp TEXT DEFAULT '',
        ayah_pekerjaan TEXT DEFAULT '',
        ibu_pekerjaan TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS student_semester_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        sem_key TEXT NOT NULL,
        tulis_json TEXT NOT NULL,
        hafalan_json TEXT NOT NULL,
        kitab_json TEXT NOT NULL,
        kelakuan TEXT DEFAULT 'B',
        kerajinan TEXT DEFAULT 'B',
        kerapihan TEXT DEFAULT 'B',
        sakit INTEGER DEFAULT 0,
        izin INTEGER DEFAULT 0,
        alpa INTEGER DEFAULT 0,
        catatan TEXT DEFAULT '',
        keputusan TEXT DEFAULT '',
        UNIQUE(student_id, sem_key)
    );

    CREATE TABLE IF NOT EXISTS student_scores_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
        class_id TEXT NOT NULL,
        sem_key TEXT NOT NULL,
        avg_score REAL DEFAULT 0,
        total_score REAL DEFAULT 0,
        UNIQUE(student_id, class_id, sem_key)
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        plain_password TEXT DEFAULT '',
        role TEXT NOT NULL, -- 'admin', 'wali', 'ustadz', 'santri'
        nama TEXT NOT NULL,
        class_id TEXT REFERENCES classes(id),
        student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
        asatidz_kode INTEGER
    );

    CREATE TABLE IF NOT EXISTS asatidz (
        kode INTEGER PRIMARY KEY,
        nama TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        alias TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS teacher_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asatidz_kode INTEGER NOT NULL REFERENCES asatidz(kode) ON DELETE CASCADE,
        class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        subject_category TEXT NOT NULL, -- 'tulis', 'hafalan', 'kitab'
        subject_index INTEGER NOT NULL, -- 0-based index
        subject_code TEXT NOT NULL,
        subject_name TEXT NOT NULL,
        subject_arab TEXT DEFAULT '',
        jk_filter TEXT DEFAULT 'ALL' -- 'ALL', 'L', 'P'
    );
    """)


def generate_unique_password(role, existing_passwords=None, seed_val=None):
    """Generate a unique, easy-to-type 6-char alphanumeric password with role prefix:
    - Wali Kelas: WKL-842
    - Ustadz Pengampu: UST-519
    - Santri: SNT-304
    """
    prefix_map = {
        "wali": "WKL",
        "ustadz": "UST",
        "santri": "SNT",
        "admin": "ADM"
    }
    prefix = prefix_map.get(role, "USR")
    used = set(existing_passwords) if existing_passwords else set()

    if seed_val is not None:
        # Deterministic initial 3-digit code (100..999) with coprime step so every account is distinct
        base_num = 100 + ((int(seed_val) * 137 + 419) % 899)
        for offset in range(900):
            num = 100 + ((base_num - 100 + offset * 73) % 900)
            candidate = f"{prefix}-{num:03d}"
            if candidate not in used:
                used.add(candidate)
                return candidate

    # Random generation when regenerating or adding new users
    for _ in range(1000):
        num = random.randint(100, 999)
        candidate = f"{prefix}-{num:03d}"
        if candidate not in used:
            used.add(candidate)
            return candidate

    # Fallback if >900 users in a single role
    chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    while True:
        suffix = "".join(random.choice(chars) for _ in range(3))
        candidate = f"{prefix}-{suffix}"
        if candidate not in used:
            used.add(candidate)
            return candidate


def _ensure_unique_user_passwords(conn):
    """Ensure every user has a populated unique plain_password and matching password_hash."""
    rows = conn.execute("SELECT id, username, role, plain_password FROM users ORDER BY id").fetchall()
    used_pw = set()
    for r in rows:
        pw = (r["plain_password"] or "").strip()
        if pw and pw not in ("ustadz123", "santri123"):
            used_pw.add(pw)

    for idx, r in enumerate(rows, 1):
        uid = r["id"]
        role = r["role"]
        pw = (r["plain_password"] or "").strip()
        if role == "admin":
            if not pw:
                conn.execute(
                    "UPDATE users SET plain_password = ?, password_hash = ? WHERE id = ?",
                    ("admin123", generate_password_hash("admin123"), uid)
                )
        else:
            if not pw or pw in ("ustadz123", "santri123"):
                new_pw = generate_unique_password(role, used_pw, seed_val=uid * 17 + idx)
                conn.execute(
                    "UPDATE users SET plain_password = ?, password_hash = ? WHERE id = ?",
                    (new_pw, generate_password_hash(new_pw), uid)
                )


def _migrate_students_columns(conn):
    """Ensure all 12 official biodata columns exist in students table and asatidz_kode/plain_password in users."""
    existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(students)").fetchall()]
    new_cols = {
        "ttl": "TEXT DEFAULT ''",
        "agama": "TEXT DEFAULT 'Islam'",
        "anak_ke": "TEXT DEFAULT ''",
        "status_keluarga": "TEXT DEFAULT 'Anak Kandung'",
        "alamat": "TEXT DEFAULT ''",
        "diterima_kelas": "TEXT DEFAULT ''",
        "diterima_tanggal": "TEXT DEFAULT ''",
        "sekolah_asal": "TEXT DEFAULT ''",
        "sekolah_asal_alamat": "TEXT DEFAULT ''",
        "ayah_nama": "TEXT DEFAULT ''",
        "ibu_nama": "TEXT DEFAULT ''",
        "ortu_alamat": "TEXT DEFAULT ''",
        "no_hp": "TEXT DEFAULT ''",
        "ayah_pekerjaan": "TEXT DEFAULT ''",
        "ibu_pekerjaan": "TEXT DEFAULT ''"
    }
    for col, col_type in new_cols.items():
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE students ADD COLUMN {col} {col_type}")

    user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "asatidz_kode" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN asatidz_kode INTEGER")
    if "plain_password" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN plain_password TEXT DEFAULT ''")


def _seed_asatidz_and_assignments(conn, used_passwords=None):
    """Populate the 44 official Asatidz accounts with unique passwords and their schedule subject assignments."""
    conn.execute("DELETE FROM teacher_assignments")
    conn.execute("DELETE FROM asatidz")
    conn.execute("DELETE FROM users WHERE role = 'ustadz'")

    if used_passwords is None:
        used_passwords = set()

    assignments = build_official_teacher_assignments()

    # Determine default class_id for each asatidz (first class they teach, or kls2)
    first_class_by_kode = {}
    for a in assignments:
        if a["asatidz_kode"] not in first_class_by_kode:
            first_class_by_kode[a["asatidz_kode"]] = a["class_id"]

    for ast in ASATIDZ_DATA:
        kode = ast["kode"]
        conn.execute("""
        INSERT INTO asatidz (kode, nama, username, alias)
        VALUES (?, ?, ?, ?)
        """, (kode, ast["nama"], ast["username"], ast["alias"]))

        default_cid = first_class_by_kode.get(kode, "kls2")
        unique_pw = generate_unique_password("ustadz", used_passwords, seed_val=100 + kode)
        pw_hash = generate_password_hash(unique_pw)
        conn.execute("""
        INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, asatidz_kode)
        VALUES (?, ?, ?, 'ustadz', ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            nama = excluded.nama,
            class_id = excluded.class_id,
            asatidz_kode = excluded.asatidz_kode
        """, (ast["username"], pw_hash, unique_pw, ast["nama"], default_cid, kode))

    # Link tatang (Wali Kelas 2) to asatidz_kode = 24 as well
    conn.execute("UPDATE users SET asatidz_kode = 24 WHERE username = 'tatang'")

    for a in assignments:
        conn.execute("""
        INSERT INTO teacher_assignments (
            asatidz_kode, class_id, subject_category, subject_index,
            subject_code, subject_name, subject_arab, jk_filter
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            a["asatidz_kode"], a["class_id"], a["subject_category"], a["subject_index"],
            a["subject_code"], a["subject_name"], a["subject_arab"], a["jk_filter"]
        ))


def init_db():
    conn = get_db()
    with conn:
        _create_tables(conn)
        _migrate_students_columns(conn)
        count = conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0]
        if count == 0:
            seed_database(conn)
        else:
            ast_count = conn.execute("SELECT COUNT(*) FROM asatidz").fetchone()[0]
            if ast_count == 0:
                _seed_asatidz_and_assignments(conn)
                # Synchronize class subjects to official 2026/2027 schedule
                for cid, subj in CURRICULUM_BY_CLASS.items():
                    conn.execute(
                        "UPDATE class_semester_config SET subjects_json = ? WHERE class_id = ?",
                        (json.dumps(subj, ensure_ascii=False), cid)
                    )
            _ensure_unique_user_passwords(conn)
    conn.close()


def seed_database(conn=None):
    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True

    with conn:
        _create_tables(conn)
        _migrate_students_columns(conn)

    with conn:
        conn.execute("DELETE FROM teacher_assignments")
        conn.execute("DELETE FROM asatidz")
        conn.execute("DELETE FROM student_semester_data")
        conn.execute("DELETE FROM users")
        conn.execute("DELETE FROM students")
        conn.execute("DELETE FROM class_semester_config")
        conn.execute("DELETE FROM classes")
        conn.execute("DELETE FROM meta")
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('students', 'users', 'student_semester_data', 'teacher_assignments')")
        except sqlite3.OperationalError:
            pass

        # Meta
        conn.execute("INSERT INTO meta (key, val) VALUES (?, ?)", ("activeSemester", "sem1"))
        conn.execute("INSERT INTO meta (key, val) VALUES (?, ?)", ("activeClassId", "kls2"))
        conn.execute("INSERT INTO meta (key, val) VALUES (?, ?)", ("logoUrl", "Ihya 'Ulumiddin.png"))
        shared_header = {
            "yayasanArab": "مؤسسة إحياء العلوم فاماريجان",
            "madrasahArab": "مدرسة الاسلامي السلفي إحياء علوم الدين",
            "statistikArab": "٥١٠٠٣٢٠٧٠٤٥٨",
            "alamatArab": "طريق فاماريجان السريع رقم ٤٢٤ قرية / منطقة فاماريجان جياميس - جاوة الغربية الرمز البريدي : ٤٦٣٨٢"
        }
        conn.execute("INSERT INTO meta (key, val) VALUES (?, ?)", ("sharedHeader", json.dumps(shared_header, ensure_ascii=False)))

        # Insert 6 Classes & their configs with unique curriculum per class
        for c in CLASSES_DATA:
            cid = c["id"]
            subjects_for_class = CURRICULUM_BY_CLASS.get(cid, DEFAULT_SUBJECTS)
            sec_b_label = "HAFALAN AL-QUR'AN" if c["tingkat"] <= 3 else "HAFALAN NADHOM"

            conn.execute("""
            INSERT INTO classes (id, nama, tingkat, wali_nama, wali_username)
            VALUES (?, ?, ?, ?, ?)
            """, (c["id"], c["nama"], c["tingkat"], c["wali_nama"], c["wali_username"]))

            # Semester 1 Config (Ganjil - Desember 2026)
            conn.execute("""
            INSERT INTO class_semester_config (
                class_id, sem_key, label, kelas_title, tahun_pelajaran, tanggal,
                wali_kelas, kepala_madrasah, arab_header_col, sec_b_indo, sec_b_arab,
                sec_c_indo, sec_c_arab, show_keputusan, subjects_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], "sem1", "Semester 1 (Ganjil)", c["nama"], "2026/2027",
                "Pamarican, 18 Desember 2026", c["wali_nama"], "Ust. TAUFIK HIDAYAT",
                "نتائج التمرين الاول", sec_b_label, "المحا فظة", "TES BACA KITAB", "قراءةالكتاب",
                0, json.dumps(subjects_for_class, ensure_ascii=False)
            ))

            # Semester 2 Config (Genap - Juni 2027)
            conn.execute("""
            INSERT INTO class_semester_config (
                class_id, sem_key, label, kelas_title, tahun_pelajaran, tanggal,
                wali_kelas, kepala_madrasah, arab_header_col, sec_b_indo, sec_b_arab,
                sec_c_indo, sec_c_arab, show_keputusan, subjects_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                c["id"], "sem2", "Semester 2 (Genap)", c["nama"], "2026/2027",
                "Pamarican, 19 Juni 2027", c["wali_nama"], "Ust. TAUFIK HIDAYAT",
                "نتائج الامتحانات", "MEMBACA + HAFALAN", "يقرأ+المحا فظة", "TES MEMBACA KITAB", "قراءة الكتاب",
                1, json.dumps(subjects_for_class, ensure_ascii=False)
            ))

        used_passwords = set()

        # Admin Account
        conn.execute("""
        INSERT INTO users (username, password_hash, plain_password, role, nama)
        VALUES (?, ?, ?, ?, ?)
        """, ("admin", generate_password_hash("admin123"), "admin123", "admin", "Administrator Pondok"))

        # Wali Kelas Accounts (wali1 s.d. wali6, tatang) with unique WKL-xxx passwords
        for w_idx, c in enumerate(CLASSES_DATA, 1):
            w_pw = generate_unique_password("wali", used_passwords, seed_val=w_idx)
            conn.execute("""
            INSERT INTO users (username, password_hash, plain_password, role, nama, class_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (c["wali_username"], generate_password_hash(w_pw), w_pw, "wali", c["wali_nama"], c["id"]))

        # 44 Official Asatidz Accounts (ust1 s.d. ust44) & Schedule Subject Assignments
        _seed_asatidz_and_assignments(conn, used_passwords)

        catatan_def = "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ"
        empty_tulis = json.dumps([0] * 12)
        empty_hafalan = json.dumps([0] * 2)
        empty_kitab = json.dumps([0] * 2)

        # Seed 63 Santri for Kelas 2 (grades initialized to 0)
        for idx, st in enumerate(STUDENTS_KLS2, 1):
            wali_name = st.get("wali", "")
            ayah_name = wali_name or "H. Abdullah"
            ibu_name = "Ibu " + (st["nama"].split()[0].title() if st.get("nama") else "Siti")
            cur = conn.execute("""
            INSERT INTO students (
                class_id, nis, nama, jk, wali, ttl, agama, anak_ke, status_keluarga,
                alamat, diterima_kelas, diterima_tanggal, sekolah_asal, sekolah_asal_alamat,
                ayah_nama, ibu_nama, ortu_alamat, no_hp, ayah_pekerjaan, ibu_pekerjaan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "kls2", st["nis"], st["nama"], st["jk"], wali_name,
                "Ciamis, 15 Juli 2011", "Islam", str((idx % 4) + 1), "Anak Kandung",
                "Pamarican, Ciamis - Jawa Barat", "Kelas 2 MISIU", "15 Juli 2026",
                "MI Salafiyah Pamarican", "Jl. Raya Pamarican No. 424",
                ayah_name, ibu_name, "Pamarican, Ciamis - Jawa Barat",
                "0812345678" + str(idx % 100).zfill(2), "Wiraswasta / Petani", "Ibu Rumah Tangga"
            ))
            student_id = cur.lastrowid

            # Santri login account with unique SNT-xxx password
            s_pw = generate_unique_password("santri", used_passwords, seed_val=500 + student_id)
            conn.execute("""
            INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, student_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (st["nis"], generate_password_hash(s_pw), s_pw, "santri", st["nama"], "kls2", student_id))

            # Sem 1 record (all 0)
            conn.execute("""
            INSERT INTO student_semester_data (
                student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
            ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, '')
            """, (student_id, "sem1", empty_tulis, empty_hafalan, empty_kitab, catatan_def))

            # Sem 2 record (all 0)
            conn.execute("""
            INSERT INTO student_semester_data (
                student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
            ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, 'Naik Kelas Ke Kelas 3')
            """, (student_id, "sem2", empty_tulis, empty_hafalan, empty_kitab, catatan_def))

        # Seed sample students for other classes
        for cid, st_list in SAMPLE_STUDENTS_OTHER.items():
            for s_idx, st in enumerate(st_list, 1):
                wali_name = st.get("wali", "")
                ayah_name = wali_name or "H. Ahmad"
                ibu_name = "Ibu " + (st["nama"].split()[0].title() if st.get("nama") else "Fatimah")
                cur = conn.execute("""
                INSERT INTO students (
                    class_id, nis, nama, jk, wali, ttl, agama, anak_ke, status_keluarga,
                    alamat, diterima_kelas, diterima_tanggal, sekolah_asal, sekolah_asal_alamat,
                    ayah_nama, ibu_nama, ortu_alamat, no_hp, ayah_pekerjaan, ibu_pekerjaan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid, st["nis"], st["nama"], st["jk"], wali_name,
                    "Ciamis, 10 Maret 2012", "Islam", str(s_idx), "Anak Kandung",
                    "Pamarican, Ciamis - Jawa Barat", f"Kelas {cid.replace('kls', '')} MISIU", "15 Juli 2026",
                    "MI Salafiyah Pamarican", "Jl. Raya Pamarican No. 424",
                    ayah_name, ibu_name, "Pamarican, Ciamis - Jawa Barat",
                    "081298765" + str(s_idx).zfill(3), "Wiraswasta", "Ibu Rumah Tangga"
                ))
                sid = cur.lastrowid
                s_pw = generate_unique_password("santri", used_passwords, seed_val=500 + sid)
                conn.execute("""
                INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, student_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (st["nis"], generate_password_hash(s_pw), s_pw, "santri", st["nama"], cid, sid))

                conn.execute("""
                INSERT INTO student_semester_data (
                    student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                    kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
                ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, '')
                """, (sid, "sem1", empty_tulis, empty_hafalan, empty_kitab, catatan_def))

                next_class = f"Naik Kelas Ke Kelas {int(cid.replace('kls', '')) + 1}"
                conn.execute("""
                INSERT INTO student_semester_data (
                    student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                    kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
                ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, ?)
                """, (sid, "sem2", empty_tulis, empty_hafalan, empty_kitab, catatan_def, next_class))

    if should_close:
        conn.close()


def get_teacher_assignments_by_kode(conn, asatidz_kode):
    if not asatidz_kode:
        return []
    rows = conn.execute("""
        SELECT ta.*, c.nama AS class_nama
        FROM teacher_assignments ta
        LEFT JOIN classes c ON c.id = ta.class_id
        WHERE ta.asatidz_kode = ?
        ORDER BY ta.class_id, ta.subject_category, ta.subject_index
    """, (asatidz_kode,)).fetchall()
    return [dict(r) for r in rows]


def authenticate_user(username, password):
    conn = get_db()
    u = username.strip().lower()
    user_row = conn.execute("SELECT * FROM users WHERE LOWER(username) = ?", (u,)).fetchone()
    if not user_row:
        # Check if username matches an asatidz alias (e.g. 'sarlan', 'alis', 'nurcholik', 'abah', etc.)
        ast_row = conn.execute("SELECT * FROM asatidz WHERE LOWER(alias) = ? OR CAST(kode AS TEXT) = ?", (u, u)).fetchone()
        if ast_row:
            user_row = conn.execute("SELECT * FROM users WHERE LOWER(username) = ?", (ast_row["username"].lower(),)).fetchone()

    if user_row and check_password_hash(user_row["password_hash"], password.strip()):
        asatidz_kode = user_row["asatidz_kode"] if "asatidz_kode" in user_row.keys() else None
        assignments = get_teacher_assignments_by_kode(conn, asatidz_kode) if asatidz_kode else []
        conn.close()
        return {
            "id": user_row["id"],
            "username": user_row["username"],
            "role": user_row["role"],
            "name": user_row["nama"],
            "classId": user_row["class_id"],
            "studentId": user_row["student_id"],
            "asatidzKode": asatidz_kode,
            "assignments": assignments,
            "nis": user_row["username"] if user_row["role"] == "santri" else None
        }
    conn.close()
    return None


def get_classes_list():
    conn = get_db()
    classes = [dict(r) for r in conn.execute("SELECT * FROM classes ORDER BY tingkat").fetchall()]
    conn.close()
    return classes


def get_student_by_id(sid):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_student_progression(student_id):
    conn = get_db()
    st = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not st:
        conn.close()
        return []

    cur_cid = st["class_id"]

    sc_rows = conn.execute("SELECT * FROM student_semester_data WHERE student_id = ?", (student_id,)).fetchall()
    sc_map = {r["sem_key"]: r for r in sc_rows}

    hist_rows = conn.execute("SELECT * FROM student_scores_history WHERE student_id = ?", (student_id,)).fetchall()
    hist_map = {(r["class_id"], r["sem_key"]): r["avg_score"] for r in hist_rows}

    conn.close()

    classes_order = ["kls1", "kls2", "kls3", "kls4", "kls5", "kls6"]
    class_names = {
        "kls1": "Kelas 1", "kls2": "Kelas 2", "kls3": "Kelas 3",
        "kls4": "Kelas 4", "kls5": "Kelas 5", "kls6": "Kelas 6"
    }

    progression = []
    for cid in classes_order:
        cname = class_names.get(cid, cid.upper())
        for sem in ["sem1", "sem2"]:
            sem_label = "Sem 1" if sem == "sem1" else "Sem 2"
            label = f"{cname} ({sem_label})"

            avg = 0.0
            graded = False

            if cid == cur_cid:
                sc = sc_map.get(sem)
                if sc:
                    tulis = json.loads(sc["tulis_json"]) if sc["tulis_json"] else []
                    hafalan = json.loads(sc["hafalan_json"]) if sc["hafalan_json"] else []
                    kitab = json.loads(sc["kitab_json"]) if sc["kitab_json"] else []
                    all_scores = [float(x) for x in (tulis + hafalan + kitab) if float(x) > 0]
                    if all_scores:
                        avg = round(sum(all_scores) / len(all_scores), 1)
                        graded = True
            elif (cid, sem) in hist_map:
                avg = float(hist_map[(cid, sem)])
                graded = avg > 0

            progression.append({
                "classId": cid,
                "className": cname,
                "semKey": sem,
                "label": label,
                "average": avg if graded else 0.0,
                "graded": graded
            })

    return progression


def get_full_state(class_id=None, user=None):
    """Retrieve full application state with strict Role-Based Access Control."""
    conn = get_db()

    my_assignments = []
    assigned_class_ids = []
    if user and user.get("asatidzKode"):
        my_assignments = get_teacher_assignments_by_kode(conn, user.get("asatidzKode"))
        for a in my_assignments:
            if a["class_id"] not in assigned_class_ids:
                assigned_class_ids.append(a["class_id"])

    # RBAC Class Lock:
    if user:
        if user.get("role") == "wali":
            # Wali Kelas is strictly locked to their assigned class
            class_id = user.get("classId") or "kls2"
        elif user.get("role") == "santri":
            # Santri is locked to their class
            class_id = user.get("classId") or "kls2"
        elif user.get("role") == "ustadz":
            if class_id and class_id in assigned_class_ids:
                pass
            elif assigned_class_ids:
                class_id = assigned_class_ids[0]
            else:
                class_id = user.get("classId") or "kls2"

    # Meta
    sem_row = conn.execute("SELECT val FROM meta WHERE key = 'activeSemester'").fetchone()
    active_sem = sem_row["val"] if sem_row else "sem1"

    cls_row = conn.execute("SELECT val FROM meta WHERE key = 'activeClassId'").fetchone()
    current_class_id = class_id or (cls_row["val"] if cls_row else "kls2")

    logo_row = conn.execute("SELECT val FROM meta WHERE key = 'logoUrl'").fetchone()
    logo_url = logo_row["val"] if logo_row else "Ihya 'Ulumiddin.png"

    hdr_row = conn.execute("SELECT val FROM meta WHERE key = 'sharedHeader'").fetchone()
    shared_header = json.loads(hdr_row["val"]) if hdr_row else {}
    shared_header["logoUrl"] = logo_url

    # Classes summary
    classes = [dict(r) for r in conn.execute("SELECT * FROM classes ORDER BY tingkat").fetchall()]

    valid_ids = [c["id"] for c in classes]
    if current_class_id not in valid_ids:
        current_class_id = "kls2"

    # Per-class summary counts for dashboard
    classes_summary = []
    for c in classes:
        cid = c["id"]
        total_st = conn.execute("SELECT COUNT(*) FROM students WHERE class_id = ?", (cid,)).fetchone()[0]
        
        graded_sem1 = conn.execute("""
            SELECT COUNT(DISTINCT d.student_id)
            FROM student_semester_data d
            JOIN students s ON s.id = d.student_id
            WHERE s.class_id = ? AND d.sem_key = 'sem1'
              AND (d.tulis_json NOT IN ('[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[0,0,0,0,0,0,0,0,0,0,0,0]'))
        """, (cid,)).fetchone()[0]

        graded_sem2 = conn.execute("""
            SELECT COUNT(DISTINCT d.student_id)
            FROM student_semester_data d
            JOIN students s ON s.id = d.student_id
            WHERE s.class_id = ? AND d.sem_key = 'sem2'
              AND (d.tulis_json NOT IN ('[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]', '[0,0,0,0,0,0,0,0,0,0,0,0]'))
        """, (cid,)).fetchone()[0]

        classes_summary.append({
            "id": cid,
            "nama": c["nama"],
            "tingkat": c["tingkat"],
            "wali_nama": c["wali_nama"],
            "wali_username": c["wali_username"],
            "total_students": total_st,
            "graded_sem1": graded_sem1,
            "graded_sem2": graded_sem2
        })

    # Active class semester configs
    cfg_rows = conn.execute("SELECT * FROM class_semester_config WHERE class_id = ?", (current_class_id,)).fetchall()
    sem_config = {}
    for r in cfg_rows:
        sem_config[r["sem_key"]] = {
            "label": r["label"],
            "kelas": r["kelas_title"],
            "tahunPelajaran": r["tahun_pelajaran"],
            "tanggal": r["tanggal"],
            "waliKelas": r["wali_kelas"],
            "kepalaMadrasah": r["kepala_madrasah"],
            "arabHeaderCol": r["arab_header_col"],
            "secBIndo": r["sec_b_indo"],
            "secBArab": r["sec_b_arab"],
            "secCIndo": r["sec_c_indo"],
            "secCArab": r["sec_c_arab"],
            "showKeputusan": bool(r["show_keputusan"]),
            "subjects": json.loads(r["subjects_json"])
        }

    # Students query: RBAC FILTER
    if user and user.get("role") == "santri" and user.get("studentId"):
        # Santri ONLY gets their own student row!
        st_rows = conn.execute("SELECT * FROM students WHERE id = ?", (user.get("studentId"),)).fetchall()
    else:
        st_rows = conn.execute("SELECT * FROM students WHERE class_id = ? ORDER BY id", (current_class_id,)).fetchall()

    student_ids = [s["id"] for s in st_rows]

    score_rows = []
    if student_ids:
        placeholders = ",".join(["?"] * len(student_ids))
        score_rows = conn.execute(f"SELECT * FROM student_semester_data WHERE student_id IN ({placeholders})", student_ids).fetchall()

    scores_by_student = {}
    for sc in score_rows:
        sid = sc["student_id"]
        if sid not in scores_by_student:
            scores_by_student[sid] = {}
        scores_by_student[sid][sc["sem_key"]] = {
            "tulis": json.loads(sc["tulis_json"]),
            "hafalan": json.loads(sc["hafalan_json"]),
            "kitab": json.loads(sc["kitab_json"]),
            "kepribadian": {
                "kelakuan": sc["kelakuan"],
                "kerajinan": sc["kerajinan"],
                "kerapihan": sc["kerapihan"]
            },
            "absensi": {
                "sakit": sc["sakit"],
                "izin": sc["izin"],
                "alpa": sc["alpa"]
            },
            "catatan": sc["catatan"],
            "keputusan": sc["keputusan"]
        }

    students = []
    default_rec = {
        "tulis": [0]*12, "hafalan": [0]*2, "kitab": [0]*2,
        "kepribadian": {"kelakuan": "B", "kerajinan": "B", "kerapihan": "B"},
        "absensi": {"sakit": 0, "izin": 0, "alpa": 0},
        "catatan": "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ",
        "keputusan": ""
    }

    for s in st_rows:
        sid = s["id"]
        st_scores = scores_by_student.get(sid, {})
        wali_val = s["ayah_nama"] if s["ayah_nama"] else (s["ibu_nama"] if s["ibu_nama"] else (s["wali"] or "-"))
        students.append({
            "id": sid,
            "classId": s["class_id"],
            "nis": s["nis"] or "",
            "nama": s["nama"] or "",
            "jk": s["jk"] or "L",
            "wali": wali_val or "-",
            "ttl": s["ttl"] or "",
            "agama": s["agama"] or "Islam",
            "anak_ke": s["anak_ke"] or "",
            "status_keluarga": s["status_keluarga"] or "Anak Kandung",
            "alamat": s["alamat"] or "",
            "diterima_kelas": s["diterima_kelas"] or "",
            "diterima_tanggal": s["diterima_tanggal"] or "",
            "sekolah_asal": s["sekolah_asal"] or "",
            "sekolah_asal_alamat": s["sekolah_asal_alamat"] or "",
            "ayah_nama": s["ayah_nama"] or "",
            "ibu_nama": s["ibu_nama"] or "",
            "ortu_alamat": s["ortu_alamat"] or "",
            "no_hp": s["no_hp"] or "",
            "ayah_pekerjaan": s["ayah_pekerjaan"] or "",
            "ibu_pekerjaan": s["ibu_pekerjaan"] or "",
            "sem1": st_scores.get("sem1", default_rec.copy()),
            "sem2": st_scores.get("sem2", default_rec.copy())
        })

    # All classes configs for settings switcher
    all_cfg_rows = conn.execute("SELECT * FROM class_semester_config").fetchall()
    all_classes_configs = {}
    for r in all_cfg_rows:
        cid = r["class_id"]
        if cid not in all_classes_configs:
            all_classes_configs[cid] = {}
        all_classes_configs[cid][r["sem_key"]] = {
            "label": r["label"],
            "kelas": r["kelas_title"],
            "tahunPelajaran": r["tahun_pelajaran"],
            "tanggal": r["tanggal"],
            "waliKelas": r["wali_kelas"],
            "kepalaMadrasah": r["kepala_madrasah"],
            "arabHeaderCol": r["arab_header_col"],
            "secBIndo": r["sec_b_indo"],
            "secBArab": r["sec_b_arab"],
            "secCIndo": r["sec_c_indo"],
            "secCArab": r["sec_c_arab"],
            "showKeputusan": bool(r["show_keputusan"]),
            "subjects": json.loads(r["subjects_json"])
        }

    # Fetch all teacher assignments joined with asatidz info
    all_ta_rows = conn.execute("""
        SELECT ta.*, a.nama AS asatidz_nama, a.username AS asatidz_username, a.alias AS asatidz_alias, c.nama AS class_nama
        FROM teacher_assignments ta
        JOIN asatidz a ON a.kode = ta.asatidz_kode
        JOIN classes c ON c.id = ta.class_id
        ORDER BY ta.class_id, ta.subject_category, ta.subject_index, ta.asatidz_kode
    """).fetchall()
    all_teacher_assignments = [dict(r) for r in all_ta_rows]

    # RBAC filter for classesSummary and allClassesConfigs
    if user and user.get("role") == "wali":
        classes_summary = [c for c in classes_summary if c["id"] == current_class_id]
        all_classes_configs = {current_class_id: all_classes_configs.get(current_class_id, {})}
        allowed_classes = [c for c in classes if c["id"] == current_class_id]
    elif user and user.get("role") == "ustadz":
        classes_summary = [c for c in classes_summary if c["id"] in assigned_class_ids]
        all_classes_configs = {cid: all_classes_configs.get(cid, {}) for cid in assigned_class_ids}
        allowed_classes = [c for c in classes if c["id"] in assigned_class_ids]
    elif user and user.get("role") == "santri":
        classes_summary = [c for c in classes_summary if c["id"] == current_class_id]
        allowed_classes = [c for c in classes if c["id"] == current_class_id]
    else:
        allowed_classes = classes

    student_progression = []
    if user and user.get("role") == "santri" and user.get("studentId"):
        student_progression = get_student_progression(user.get("studentId"))

    accounts_data = None
    if not user or user.get("role") == "admin":
        accounts_data = get_all_accounts_for_admin(conn)

    conn.close()
    return {
        "activeClassId": current_class_id,
        "activeSemester": active_sem,
        "classes": allowed_classes,
        "classesSummary": classes_summary,
        "sharedHeader": shared_header,
        "semConfig": sem_config,
        "allClassesConfigs": all_classes_configs,
        "students": students,
        "studentProgression": student_progression,
        "asatidzList": ASATIDZ_DATA,
        "myAssignments": my_assignments,
        "allTeacherAssignments": all_teacher_assignments,
        "jadwalResmi": JADWAL_RESMI_DATA,
        "subjectCodesMap": SUBJECT_CODES_MAP,
        "accountsData": accounts_data
    }


def get_all_accounts_for_admin(conn=None):
    """Return all Wali Kelas, Ustadz Pengampu, and Santri accounts with unique passwords for Super Admin."""
    should_close = False
    if conn is None:
        conn = get_db()
        should_close = True

    _ensure_unique_user_passwords(conn)

    # 1. Wali Kelas Accounts
    wali_rows = conn.execute("""
        SELECT u.id, u.username, u.plain_password, u.role, u.nama, u.class_id, u.asatidz_kode,
               c.nama AS class_nama, c.tingkat
        FROM users u
        LEFT JOIN classes c ON c.id = u.class_id
        WHERE u.role = 'wali'
        ORDER BY c.tingkat, u.id
    """).fetchall()
    wali_list = [dict(r) for r in wali_rows]

    # 2. Ustadz Pengampu Accounts (44 Asatidz)
    ustadz_rows = conn.execute("""
        SELECT u.id, u.username, u.plain_password, u.role, u.nama, u.class_id, u.asatidz_kode,
               a.kode, a.alias
        FROM users u
        LEFT JOIN asatidz a ON a.kode = u.asatidz_kode
        WHERE u.role = 'ustadz'
        ORDER BY COALESCE(a.kode, u.id)
    """).fetchall()

    ta_rows = conn.execute("""
        SELECT ta.*, c.nama AS class_nama
        FROM teacher_assignments ta
        LEFT JOIN classes c ON c.id = ta.class_id
        ORDER BY ta.asatidz_kode, ta.class_id, ta.subject_category, ta.subject_index
    """).fetchall()

    ta_by_kode = {}
    for t in ta_rows:
        kd = t["asatidz_kode"]
        if kd not in ta_by_kode:
            ta_by_kode[kd] = []
        ta_by_kode[kd].append(dict(t))

    ustadz_list = []
    for r in ustadz_rows:
        d = dict(r)
        kd = d.get("kode") or d.get("asatidz_kode")
        asg_list = ta_by_kode.get(kd, [])
        # Build readable summary of subjects & classes taught
        summary_parts = []
        classes_set = []
        for a in asg_list:
            cn = (a.get("class_nama") or a.get("class_id") or "").replace(" MISIU", "")
            if cn and cn not in classes_set:
                classes_set.append(cn)
            jk_tag = f" ({'Putra' if a.get('jk_filter') == 'L' else 'Putri'})" if a.get("jk_filter") in ("L", "P") else ""
            item_str = f"{a.get('subject_name')} - {cn}{jk_tag}"
            if item_str not in summary_parts:
                summary_parts.append(item_str)
        d["assignments"] = asg_list
        d["classes_taught"] = ", ".join(classes_set) if classes_set else "-"
        d["subjects_summary"] = "; ".join(summary_parts) if summary_parts else "Pengajar Umum / Cadangan"
        ustadz_list.append(d)

    # 3. Santri Accounts
    santri_rows = conn.execute("""
        SELECT u.id, u.username, u.plain_password, u.role, u.nama, u.class_id, u.student_id,
               s.nis, s.jk, s.wali, s.ayah_nama, s.ibu_nama,
               c.nama AS class_nama, c.tingkat
        FROM users u
        LEFT JOIN students s ON s.id = u.student_id
        LEFT JOIN classes c ON c.id = COALESCE(s.class_id, u.class_id)
        WHERE u.role = 'santri'
        ORDER BY COALESCE(c.tingkat, 99), s.nama, u.nama
    """).fetchall()
    santri_list = []
    for r in santri_rows:
        d = dict(r)
        d["nis"] = d.get("nis") or d.get("username")
        d["class_nama"] = d.get("class_nama") or f"Kelas {(d.get('class_id') or 'kls2').replace('kls', '')} MISIU"
        santri_list.append(d)

    if should_close:
        conn.close()

    return {
        "wali": wali_list,
        "ustadz": ustadz_list,
        "santri": santri_list
    }


def admin_update_user_password(user_id, new_password):
    """Allow Super Admin to manually edit or set a specific user's unique password."""
    pw_clean = str(new_password or "").strip()
    if len(pw_clean) < 4:
        return False, "Password minimal 4 karakter."
    conn = get_db()
    row = conn.execute("SELECT id, username, nama, role FROM users WHERE id = ?", (int(user_id),)).fetchone()
    if not row:
        conn.close()
        return False, "Akun pengguna tidak ditemukan."
    with conn:
        conn.execute(
            "UPDATE users SET plain_password = ?, password_hash = ? WHERE id = ?",
            (pw_clean, generate_password_hash(pw_clean), int(user_id))
        )
    conn.close()
    return True, pw_clean


def admin_regenerate_passwords(target_role="ALL", class_id=None, user_id=None):
    """Regenerate unique passwords (WKL-xxx, UST-xxx, SNT-xxx) for one user, a role category, or all accounts."""
    conn = get_db()
    all_rows = conn.execute("SELECT id, role, class_id, plain_password FROM users").fetchall()
    used_pw = {r["plain_password"] for r in all_rows if r["plain_password"]}

    if user_id:
        target_rows = [r for r in all_rows if r["id"] == int(user_id) and r["role"] != "admin"]
    else:
        target_rows = []
        for r in all_rows:
            if r["role"] == "admin":
                continue
            if target_role != "ALL" and r["role"] != target_role:
                continue
            if target_role == "santri" and class_id and class_id != "ALL" and r["class_id"] != class_id:
                continue
            target_rows.append(r)

    updated_count = 0
    last_new_pw = ""
    with conn:
        for r in target_rows:
            new_pw = generate_unique_password(r["role"], used_pw, seed_val=None)
            conn.execute(
                "UPDATE users SET plain_password = ?, password_hash = ? WHERE id = ?",
                (new_pw, generate_password_hash(new_pw), r["id"])
            )
            last_new_pw = new_pw
            updated_count += 1

    conn.close()
    return True, updated_count, last_new_pw


def save_subject_scores(class_id, sem_key, subject_category, subject_index, scores, allowed_jk="ALL"):
    """Save scores for a single subject across students in a class without overwriting other subjects."""
    if subject_category not in ("tulis", "hafalan", "kitab"):
        raise ValueError("Kategori mata pelajaran tidak valid.")

    col_map = {
        "tulis": ("tulis_json", 12),
        "hafalan": ("hafalan_json", 2),
        "kitab": ("kitab_json", 2),
    }
    col_name, arr_len = col_map[subject_category]
    idx = int(subject_index)
    if idx < 0 or idx >= arr_len:
        raise ValueError("Indeks mata pelajaran di luar batas.")

    conn = get_db()
    updated_count = 0
    with conn:
        for item in scores:
            sid = item.get("id")
            nis = str(item.get("nis", "")).strip()
            raw_val = item.get("score", 0)
            try:
                val = int(round(float(raw_val)))
            except Exception:
                val = 0
            val = max(0, min(100, val))

            st_row = None
            if sid:
                st_row = conn.execute("SELECT id, class_id, jk FROM students WHERE id = ? AND class_id = ?", (int(sid), class_id)).fetchone()
            if not st_row and nis:
                st_row = conn.execute("SELECT id, class_id, jk FROM students WHERE nis = ? AND class_id = ?", (nis, class_id)).fetchone()
            if not st_row:
                continue

            if allowed_jk in ("L", "P") and (st_row["jk"] or "L").upper() != allowed_jk:
                continue

            real_sid = st_row["id"]
            sc_row = conn.execute(
                "SELECT tulis_json, hafalan_json, kitab_json FROM student_semester_data WHERE student_id = ? AND sem_key = ?",
                (real_sid, sem_key)
            ).fetchone()

            if sc_row:
                arr = json.loads(sc_row[col_name]) if sc_row[col_name] else [0] * arr_len
                while len(arr) < arr_len:
                    arr.append(0)
                arr[idx] = val
                conn.execute(
                    f"UPDATE student_semester_data SET {col_name} = ? WHERE student_id = ? AND sem_key = ?",
                    (json.dumps(arr), real_sid, sem_key)
                )
            else:
                tulis_arr = [0] * 12
                hafalan_arr = [0] * 2
                kitab_arr = [0] * 2
                if subject_category == "tulis":
                    tulis_arr[idx] = val
                elif subject_category == "hafalan":
                    hafalan_arr[idx] = val
                else:
                    kitab_arr[idx] = val
                catatan_def = "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ"
                conn.execute("""
                INSERT INTO student_semester_data (
                    student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                    kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
                ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, '')
                """, (real_sid, sem_key, json.dumps(tulis_arr), json.dumps(hafalan_arr), json.dumps(kitab_arr), catatan_def))
            updated_count += 1
    conn.close()
    return updated_count


def save_single_student_scores(data):
    sid = data.get("id")
    sem_key = data.get("semKey", "sem1")
    nama = data.get("nama", "").strip()
    wali = data.get("wali", "").strip()
    jk = data.get("jk", "L")

    conn = get_db()
    with conn:
        if nama:
            conn.execute("UPDATE students SET nama = ? WHERE id = ?", (nama, sid))
            conn.execute("UPDATE users SET nama = ? WHERE student_id = ?", (nama, sid))
        if wali:
            conn.execute("UPDATE students SET wali = ? WHERE id = ?", (wali, sid))
        if jk:
            conn.execute("UPDATE students SET jk = ? WHERE id = ?", (jk, sid))

        kepribadian = data.get("kepribadian", {})
        absensi = data.get("absensi", {})

        conn.execute("""
        INSERT INTO student_semester_data (
            student_id, sem_key, tulis_json, hafalan_json, kitab_json,
            kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, sem_key) DO UPDATE SET
            tulis_json = excluded.tulis_json,
            hafalan_json = excluded.hafalan_json,
            kitab_json = excluded.kitab_json,
            kelakuan = excluded.kelakuan,
            kerajinan = excluded.kerajinan,
            kerapihan = excluded.kerapihan,
            sakit = excluded.sakit,
            izin = excluded.izin,
            alpa = excluded.alpa,
            catatan = excluded.catatan,
            keputusan = excluded.keputusan
        """, (
            sid,
            sem_key,
            json.dumps(data.get("tulis", [0]*12)),
            json.dumps(data.get("hafalan", [0]*2)),
            json.dumps(data.get("kitab", [0]*2)),
            kepribadian.get("kelakuan", "B"),
            kepribadian.get("kerajinan", "B"),
            kepribadian.get("kerapihan", "B"),
            absensi.get("sakit", 0),
            absensi.get("izin", 0),
            absensi.get("alpa", 0),
            data.get("catatan", ""),
            data.get("keputusan", "")
        ))
    conn.close()


def save_bulk_scores(class_id, sem_key, items):
    """Save an entire class spreadsheet grid of student scores in one atomic transaction."""
    conn = get_db()
    with conn:
        for item in items:
            sid = item.get("id")
            if not sid:
                continue

            nama = item.get("nama")
            wali = item.get("wali")
            if nama:
                conn.execute("UPDATE students SET nama = ? WHERE id = ?", (nama.strip(), sid))
                conn.execute("UPDATE users SET nama = ? WHERE student_id = ?", (nama.strip(), sid))
            if wali is not None:
                conn.execute("UPDATE students SET wali = ? WHERE id = ?", (wali.strip(), sid))

            kep = item.get("kepribadian", {})
            absn = item.get("absensi", {})

            conn.execute("""
            INSERT INTO student_semester_data (
                student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, sem_key) DO UPDATE SET
                tulis_json = excluded.tulis_json,
                hafalan_json = excluded.hafalan_json,
                kitab_json = excluded.kitab_json,
                kelakuan = excluded.kelakuan,
                kerajinan = excluded.kerajinan,
                kerapihan = excluded.kerapihan,
                sakit = excluded.sakit,
                izin = excluded.izin,
                alpa = excluded.alpa,
                catatan = excluded.catatan,
                keputusan = excluded.keputusan
            """, (
                sid,
                sem_key,
                json.dumps(item.get("tulis", [0]*12)),
                json.dumps(item.get("hafalan", [0]*2)),
                json.dumps(item.get("kitab", [0]*2)),
                kep.get("kelakuan", "B"),
                kep.get("kerajinan", "B"),
                kep.get("kerapihan", "B"),
                absn.get("sakit", 0),
                absn.get("izin", 0),
                absn.get("alpa", 0),
                item.get("catatan", "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ"),
                item.get("keputusan", "")
            ))
    conn.close()


def add_student(
    class_id, nis, nama, jk="L", wali="",
    ttl="", agama="Islam", anak_ke="", status_keluarga="Anak Kandung",
    alamat="", diterima_kelas="", diterima_tanggal="",
    sekolah_asal="", sekolah_asal_alamat="",
    ayah_nama="", ibu_nama="", ortu_alamat="", no_hp="",
    ayah_pekerjaan="", ibu_pekerjaan="", **kwargs
):
    conn = get_db()
    with conn:
        nis_clean = str(nis).strip()
        nama_clean = str(nama).strip()
        jk_clean = str(jk).strip().upper() if str(jk).strip() else "L"
        if jk_clean not in ["L", "P"]:
            jk_clean = "L"

        ayah_clean = str(ayah_nama).strip() if ayah_nama else ""
        ibu_clean = str(ibu_nama).strip() if ibu_nama else ""
        wali_clean = str(wali).strip() if wali else ""
        if not wali_clean:
            wali_clean = ayah_clean or ibu_clean or "-"

        cur = conn.execute("""
        INSERT INTO students (
            class_id, nis, nama, jk, wali, ttl, agama, anak_ke, status_keluarga,
            alamat, diterima_kelas, diterima_tanggal, sekolah_asal, sekolah_asal_alamat,
            ayah_nama, ibu_nama, ortu_alamat, no_hp, ayah_pekerjaan, ibu_pekerjaan
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            class_id, nis_clean, nama_clean, jk_clean, wali_clean,
            str(ttl or "").strip(), str(agama or "Islam").strip(),
            str(anak_ke or "").strip(), str(status_keluarga or "Anak Kandung").strip(),
            str(alamat or "").strip(), str(diterima_kelas or "").strip(),
            str(diterima_tanggal or "").strip(), str(sekolah_asal or "").strip(),
            str(sekolah_asal_alamat or "").strip(), ayah_clean, ibu_clean,
            str(ortu_alamat or "").strip(), str(no_hp or "").strip(),
            str(ayah_pekerjaan or "").strip(), str(ibu_pekerjaan or "").strip()
        ))
        sid = cur.lastrowid

        used_pw = {r[0] for r in conn.execute("SELECT plain_password FROM users WHERE plain_password != ''").fetchall()}
        s_pw = generate_unique_password("santri", used_pw, seed_val=500 + sid)
        conn.execute("""
        INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, student_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            nama = excluded.nama,
            class_id = excluded.class_id,
            student_id = excluded.student_id
        """, (nis_clean, generate_password_hash(s_pw), s_pw, "santri", nama_clean, class_id, sid))

        empty_scores = [0] * 12
        empty_two = [0] * 2
        catatan_def = "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ"

        conn.execute("""
        INSERT INTO student_semester_data (
            student_id, sem_key, tulis_json, hafalan_json, kitab_json,
            kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
        ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, '')
        ON CONFLICT(student_id, sem_key) DO NOTHING
        """, (sid, "sem1", json.dumps(empty_scores), json.dumps(empty_two), json.dumps(empty_two), catatan_def))

        next_c = int(class_id.replace("kls", "")) + 1 if "kls" in class_id else 3
        conn.execute("""
        INSERT INTO student_semester_data (
            student_id, sem_key, tulis_json, hafalan_json, kitab_json,
            kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
        ) VALUES (?, ?, ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, ?)
        ON CONFLICT(student_id, sem_key) DO NOTHING
        """, (sid, "sem2", json.dumps(empty_scores), json.dumps(empty_two), json.dumps(empty_two), catatan_def, f"Naik Kelas Ke Kelas {next_c}"))

    conn.close()
    return sid


def update_student(
    student_id, nis, nama, jk="L", wali="",
    ttl="", agama="Islam", anak_ke="", status_keluarga="Anak Kandung",
    alamat="", diterima_kelas="", diterima_tanggal="",
    sekolah_asal="", sekolah_asal_alamat="",
    ayah_nama="", ibu_nama="", ortu_alamat="", no_hp="",
    ayah_pekerjaan="", ibu_pekerjaan="", **kwargs
):
    conn = get_db()
    with conn:
        nis_clean = str(nis).strip()
        nama_clean = str(nama).strip()
        jk_clean = str(jk).strip().upper() if str(jk).strip() else "L"
        if jk_clean not in ["L", "P"]:
            jk_clean = "L"

        ayah_clean = str(ayah_nama).strip() if ayah_nama else ""
        ibu_clean = str(ibu_nama).strip() if ibu_nama else ""
        wali_clean = str(wali).strip() if wali else ""
        if not wali_clean:
            wali_clean = ayah_clean or ibu_clean or "-"

        conn.execute("""
        UPDATE students SET
            nis = ?, nama = ?, jk = ?, wali = ?,
            ttl = ?, agama = ?, anak_ke = ?, status_keluarga = ?,
            alamat = ?, diterima_kelas = ?, diterima_tanggal = ?,
            sekolah_asal = ?, sekolah_asal_alamat = ?,
            ayah_nama = ?, ibu_nama = ?, ortu_alamat = ?, no_hp = ?,
            ayah_pekerjaan = ?, ibu_pekerjaan = ?
        WHERE id = ?
        """, (
            nis_clean, nama_clean, jk_clean, wali_clean,
            str(ttl or "").strip(), str(agama or "Islam").strip(),
            str(anak_ke or "").strip(), str(status_keluarga or "Anak Kandung").strip(),
            str(alamat or "").strip(), str(diterima_kelas or "").strip(),
            str(diterima_tanggal or "").strip(), str(sekolah_asal or "").strip(),
            str(sekolah_asal_alamat or "").strip(), ayah_clean, ibu_clean,
            str(ortu_alamat or "").strip(), str(no_hp or "").strip(),
            str(ayah_pekerjaan or "").strip(), str(ibu_pekerjaan or "").strip(),
            student_id
        ))

        conn.execute("""
        UPDATE users SET username = ?, nama = ? WHERE student_id = ?
        """, (nis_clean, nama_clean, student_id))
    conn.close()


def import_students(class_id, rows):
    """Import student records. If NIS already exists, updates biodata; if new, creates student + account + semester records."""
    conn = get_db()
    success_count = 0
    errors = []

    for idx, r in enumerate(rows, 1):
        nis = str(r.get("nis", "")).strip()
        nama = str(r.get("nama", "")).strip()
        if not nis or not nama:
            continue

        jk = str(r.get("jk", "L")).strip().upper()
        if jk not in ["L", "P"]:
            jk = "L"

        ayah = str(r.get("ayah_nama", "")).strip()
        ibu = str(r.get("ibu_nama", "")).strip()
        wali = str(r.get("wali", "")).strip()
        if not wali:
            wali = ayah or ibu or "-"

        ttl = str(r.get("ttl", "")).strip()
        agama = str(r.get("agama", "Islam")).strip() or "Islam"
        anak_ke = str(r.get("anak_ke", "")).strip()
        status_keluarga = str(r.get("status_keluarga", "Anak Kandung")).strip() or "Anak Kandung"
        alamat = str(r.get("alamat", "")).strip()
        diterima_kelas = str(r.get("diterima_kelas", "")).strip()
        diterima_tanggal = str(r.get("diterima_tanggal", "")).strip()
        sekolah_asal = str(r.get("sekolah_asal", "")).strip()
        sekolah_asal_alamat = str(r.get("sekolah_asal_alamat", "")).strip()
        ortu_alamat = str(r.get("ortu_alamat", "")).strip()
        no_hp = str(r.get("no_hp", "")).strip()
        ayah_pekerjaan = str(r.get("ayah_pekerjaan", "")).strip()
        ibu_pekerjaan = str(r.get("ibu_pekerjaan", "")).strip()

        try:
            with conn:
                existing = conn.execute("SELECT id FROM students WHERE nis = ?", (nis,)).fetchone()
                if existing:
                    sid = existing["id"]
                    conn.execute("""
                    UPDATE students SET
                        class_id = ?, nama = ?, jk = ?, wali = ?,
                        ttl = ?, agama = ?, anak_ke = ?, status_keluarga = ?,
                        alamat = ?, diterima_kelas = ?, diterima_tanggal = ?,
                        sekolah_asal = ?, sekolah_asal_alamat = ?,
                        ayah_nama = ?, ibu_nama = ?, ortu_alamat = ?, no_hp = ?,
                        ayah_pekerjaan = ?, ibu_pekerjaan = ?
                    WHERE id = ?
                    """, (
                        class_id, nama, jk, wali,
                        ttl, agama, anak_ke, status_keluarga,
                        alamat, diterima_kelas, diterima_tanggal,
                        sekolah_asal, sekolah_asal_alamat,
                        ayah, ibu, ortu_alamat, no_hp,
                        ayah_pekerjaan, ibu_pekerjaan,
                        sid
                    ))
                    conn.execute("UPDATE users SET nama = ?, class_id = ? WHERE student_id = ?", (nama, class_id, sid))
                else:
                    cur = conn.execute("""
                    INSERT INTO students (
                        class_id, nis, nama, jk, wali,
                        ttl, agama, anak_ke, status_keluarga,
                        alamat, diterima_kelas, diterima_tanggal,
                        sekolah_asal, sekolah_asal_alamat,
                        ayah_nama, ibu_nama, ortu_alamat, no_hp,
                        ayah_pekerjaan, ibu_pekerjaan
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        class_id, nis, nama, jk, wali,
                        ttl, agama, anak_ke, status_keluarga,
                        alamat, diterima_kelas, diterima_tanggal,
                        sekolah_asal, sekolah_asal_alamat,
                        ayah, ibu, ortu_alamat, no_hp,
                        ayah_pekerjaan, ibu_pekerjaan
                    ))
                    sid = cur.lastrowid
                    used_pw = {r[0] for r in conn.execute("SELECT plain_password FROM users WHERE plain_password != ''").fetchall()}
                    s_pw = generate_unique_password("santri", used_pw, seed_val=500 + sid)
                    conn.execute("""
                    INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, student_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET nama = excluded.nama, class_id = excluded.class_id, student_id = excluded.student_id
                    """, (nis, generate_password_hash(s_pw), s_pw, "santri", nama, class_id, sid))

                    empty_scores = json.dumps([0] * 12)
                    empty_two = json.dumps([0] * 2)
                    catatan_def = "العِلْمُ بِالتَّعَلُّمِ، وَالْبَرَكَةُ بِالْخِدْمَةِ، وَالْمَنْفَعَةُ بِالطَّاعَةِ"
                    conn.execute("""
                    INSERT INTO student_semester_data (student_id, sem_key, tulis_json, hafalan_json, kitab_json, kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan)
                    VALUES (?, 'sem1', ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, '')
                    ON CONFLICT(student_id, sem_key) DO NOTHING
                    """, (sid, empty_scores, empty_two, empty_two, catatan_def))
                    next_c = int(class_id.replace("kls", "")) + 1 if "kls" in class_id else 3
                    conn.execute("""
                    INSERT INTO student_semester_data (student_id, sem_key, tulis_json, hafalan_json, kitab_json, kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan)
                    VALUES (?, 'sem2', ?, ?, ?, 'B', 'B', 'B', 0, 0, 0, ?, ?)
                    ON CONFLICT(student_id, sem_key) DO NOTHING
                    """, (sid, empty_scores, empty_two, empty_two, catatan_def, f"Naik Kelas Ke Kelas {next_c}"))
                success_count += 1
        except Exception as e:
            errors.append(f"Baris {idx} ({nis} - {nama}): {str(e)}")

    conn.close()
    return success_count, errors


def delete_student(student_id):
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.close()


def save_class_config(class_id, sem_key, cfg):
    conn = get_db()
    with conn:
        conn.execute("""
        UPDATE class_semester_config SET
            kelas_title = ?,
            tahun_pelajaran = ?,
            tanggal = ?,
            wali_kelas = ?,
            kepala_madrasah = ?
        WHERE class_id = ? AND sem_key = ?
        """, (
            cfg.get("kelas", ""),
            cfg.get("tahunPelajaran", ""),
            cfg.get("tanggal", ""),
            cfg.get("waliKelas", ""),
            cfg.get("kepalaMadrasah", ""),
            class_id,
            sem_key
        ))
        if cfg.get("waliKelas"):
            conn.execute("UPDATE classes SET wali_nama = ? WHERE id = ?", (cfg.get("waliKelas"), class_id))
            conn.execute("UPDATE users SET nama = ? WHERE class_id = ? AND role = 'wali'", (cfg.get("waliKelas"), class_id))
    conn.close()


def save_subjects(class_id, sem_key, subjects):
    conn = get_db()
    with conn:
        conn.execute("""
        UPDATE class_semester_config SET subjects_json = ? WHERE class_id = ? AND sem_key = ?
        """, (json.dumps(subjects, ensure_ascii=False), class_id, sem_key))
    conn.close()


def save_active_semester(sem_key):
    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO meta (key, val) VALUES ('activeSemester', ?)
        ON CONFLICT(key) DO UPDATE SET val = excluded.val
        """, (sem_key,))
    conn.close()


def save_active_class(class_id):
    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO meta (key, val) VALUES ('activeClassId', ?)
        ON CONFLICT(key) DO UPDATE SET val = excluded.val
        """, (class_id,))
    conn.close()


def update_logo_url(logo_url):
    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO meta (key, val) VALUES ('logoUrl', ?)
        ON CONFLICT(key) DO UPDATE SET val = excluded.val
        """, (logo_url,))
    conn.close()


def update_user_password(user_id, old_password, new_password):
    """Change user password with old password verification."""
    if not new_password or len(new_password.strip()) < 4:
        return False, "Password baru minimal 4 karakter."
    conn = get_db()
    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user_row:
        conn.close()
        return False, "Pengguna tidak ditemukan."
    if not check_password_hash(user_row["password_hash"], old_password.strip()):
        conn.close()
        return False, "Password lama salah."

    pw_clean = new_password.strip()
    new_hash = generate_password_hash(pw_clean)
    with conn:
        conn.execute("UPDATE users SET password_hash = ?, plain_password = ? WHERE id = ?", (new_hash, pw_clean, user_id))
    conn.close()
    return True, "Password berhasil diperbarui."


def export_backup_data(class_id=None):
    """Export full database state or class-specific data for backup."""
    conn = get_db()
    meta_rows = [dict(r) for r in conn.execute("SELECT * FROM meta").fetchall()]
    classes_rows = [dict(r) for r in conn.execute("SELECT * FROM classes").fetchall()]
    cfg_rows = [dict(r) for r in conn.execute("SELECT * FROM class_semester_config").fetchall()]
    
    if class_id:
        st_rows = [dict(r) for r in conn.execute("SELECT * FROM students WHERE class_id = ?", (class_id,)).fetchall()]
        st_ids = [s["id"] for s in st_rows]
        if st_ids:
            placeholders = ",".join(["?"] * len(st_ids))
            sc_rows = [dict(r) for r in conn.execute(f"SELECT * FROM student_semester_data WHERE student_id IN ({placeholders})", st_ids).fetchall()]
        else:
            sc_rows = []
    else:
        st_rows = [dict(r) for r in conn.execute("SELECT * FROM students").fetchall()]
        sc_rows = [dict(r) for r in conn.execute("SELECT * FROM student_semester_data").fetchall()]

    conn.close()
    return {
        "version": "1.0",
        "timestamp": "2026-11-13",
        "targetClassId": class_id,
        "meta": meta_rows,
        "classes": classes_rows,
        "classSemesterConfig": cfg_rows,
        "students": st_rows,
        "studentSemesterData": sc_rows
    }


def restore_backup_data(backup_data, user=None):
    """Restore database state from backup JSON. Restricted to user's class if role is 'wali'."""
    if not isinstance(backup_data, dict):
        return False, "Format file backup tidak valid."

    students = backup_data.get("students", [])
    sem_data = backup_data.get("studentSemesterData", [])
    configs = backup_data.get("classSemesterConfig", [])

    conn = get_db()
    restored_students_count = 0

    with conn:
        # If admin and backup has configs, restore configs
        if (not user or user.get("role") == "admin") and configs:
            for cfg in configs:
                conn.execute("""
                INSERT INTO class_semester_config (
                    class_id, sem_key, label, kelas_title, tahun_pelajaran, tanggal,
                    wali_kelas, kepala_madrasah, arab_header_col, sec_b_indo, sec_b_arab,
                    sec_c_indo, sec_c_arab, show_keputusan, subjects_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(class_id, sem_key) DO UPDATE SET
                    label = excluded.label,
                    kelas_title = excluded.kelas_title,
                    tahun_pelajaran = excluded.tahun_pelajaran,
                    tanggal = excluded.tanggal,
                    wali_kelas = excluded.wali_kelas,
                    kepala_madrasah = excluded.kepala_madrasah,
                    arab_header_col = excluded.arab_header_col,
                    sec_b_indo = excluded.sec_b_indo,
                    sec_b_arab = excluded.sec_b_arab,
                    sec_c_indo = excluded.sec_c_indo,
                    sec_c_arab = excluded.sec_c_arab,
                    show_keputusan = excluded.show_keputusan,
                    subjects_json = excluded.subjects_json
                """, (
                    cfg["class_id"], cfg["sem_key"], cfg["label"], cfg["kelas_title"],
                    cfg["tahun_pelajaran"], cfg["tanggal"], cfg["wali_kelas"],
                    cfg["kepala_madrasah"], cfg["arab_header_col"], cfg["sec_b_indo"],
                    cfg["sec_b_arab"], cfg["sec_c_indo"], cfg["sec_c_arab"],
                    cfg["show_keputusan"], cfg["subjects_json"]
                ))

        # Restore students and their semester data
        st_id_map = {} # old_id -> new_id
        for st in students:
            cid = st.get("class_id", "kls2")
            if user and user.get("role") == "wali" and cid != user.get("classId"):
                continue # Skip classes not owned by wali

            nis = str(st.get("nis", "")).strip()
            nama = str(st.get("nama", "")).strip()
            if not nis or not nama:
                continue

            existing = conn.execute("SELECT id FROM students WHERE nis = ?", (nis,)).fetchone()
            if existing:
                sid = existing["id"]
                conn.execute("""
                UPDATE students SET
                    class_id = ?, nama = ?, jk = ?, wali = ?, ttl = ?, agama = ?,
                    anak_ke = ?, status_keluarga = ?, alamat = ?, diterima_kelas = ?,
                    diterima_tanggal = ?, sekolah_asal = ?, sekolah_asal_alamat = ?,
                    ayah_nama = ?, ibu_nama = ?, ortu_alamat = ?, no_hp = ?,
                    ayah_pekerjaan = ?, ibu_pekerjaan = ?
                WHERE id = ?
                """, (
                    cid, nama, st.get("jk", "L"), st.get("wali", ""), st.get("ttl", ""),
                    st.get("agama", "Islam"), st.get("anak_ke", ""), st.get("status_keluarga", "Anak Kandung"),
                    st.get("alamat", ""), st.get("diterima_kelas", ""), st.get("diterima_tanggal", ""),
                    st.get("sekolah_asal", ""), st.get("sekolah_asal_alamat", ""),
                    st.get("ayah_nama", ""), st.get("ibu_nama", ""), st.get("ortu_alamat", ""),
                    st.get("no_hp", ""), st.get("ayah_pekerjaan", ""), st.get("ibu_pekerjaan", ""),
                    sid
                ))
            else:
                cur = conn.execute("""
                INSERT INTO students (
                    class_id, nis, nama, jk, wali, ttl, agama,
                    anak_ke, status_keluarga, alamat, diterima_kelas,
                    diterima_tanggal, sekolah_asal, sekolah_asal_alamat,
                    ayah_nama, ibu_nama, ortu_alamat, no_hp,
                    ayah_pekerjaan, ibu_pekerjaan
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cid, nis, nama, st.get("jk", "L"), st.get("wali", ""), st.get("ttl", ""),
                    st.get("agama", "Islam"), st.get("anak_ke", ""), st.get("status_keluarga", "Anak Kandung"),
                    st.get("alamat", ""), st.get("diterima_kelas", ""), st.get("diterima_tanggal", ""),
                    st.get("sekolah_asal", ""), st.get("sekolah_asal_alamat", ""),
                    st.get("ayah_nama", ""), st.get("ibu_nama", ""), st.get("ortu_alamat", ""),
                    st.get("no_hp", ""), st.get("ayah_pekerjaan", ""), st.get("ibu_pekerjaan", "")
                ))
                sid = cur.lastrowid
                used_pw = {r[0] for r in conn.execute("SELECT plain_password FROM users WHERE plain_password != ''").fetchall()}
                s_pw = generate_unique_password("santri", used_pw, seed_val=500 + sid)
                conn.execute("""
                INSERT INTO users (username, password_hash, plain_password, role, nama, class_id, student_id)
                VALUES (?, ?, ?, 'santri', ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET nama = excluded.nama, class_id = excluded.class_id, student_id = excluded.student_id
                """, (nis, generate_password_hash(s_pw), s_pw, nama, cid, sid))

            old_id = st.get("id")
            if old_id:
                st_id_map[old_id] = sid
            st_id_map[f"nis_{nis}"] = sid
            restored_students_count += 1

        # Restore semester data
        for sd in sem_data:
            target_sid = None
            if sd.get("student_id") in st_id_map:
                target_sid = st_id_map[sd.get("student_id")]
            elif sd.get("nis") and f"nis_{sd.get('nis')}" in st_id_map:
                target_sid = st_id_map[f"nis_{sd.get('nis')}"]

            if not target_sid:
                continue

            conn.execute("""
            INSERT INTO student_semester_data (
                student_id, sem_key, tulis_json, hafalan_json, kitab_json,
                kelakuan, kerajinan, kerapihan, sakit, izin, alpa, catatan, keputusan
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id, sem_key) DO UPDATE SET
                tulis_json = excluded.tulis_json,
                hafalan_json = excluded.hafalan_json,
                kitab_json = excluded.kitab_json,
                kelakuan = excluded.kelakuan,
                kerajinan = excluded.kerajinan,
                kerapihan = excluded.kerapihan,
                sakit = excluded.sakit,
                izin = excluded.izin,
                alpa = excluded.alpa,
                catatan = excluded.catatan,
                keputusan = excluded.keputusan
            """, (
                target_sid, sd.get("sem_key", "sem1"),
                sd.get("tulis_json", json.dumps([0]*12)),
                sd.get("hafalan_json", json.dumps([0]*2)),
                sd.get("kitab_json", json.dumps([0]*2)),
                sd.get("kelakuan", "B"), sd.get("kerajinan", "B"), sd.get("kerapihan", "B"),
                sd.get("sakit", 0), sd.get("izin", 0), sd.get("alpa", 0),
                sd.get("catatan", ""), sd.get("keputusan", "")
            ))

    conn.close()
    return True, f"Berhasil merestore data {restored_students_count} santri beserta seluruh nilai rapor."


def update_shared_header(header_data):
    conn = get_db()
    with conn:
        conn.execute("""
        INSERT INTO meta (key, val) VALUES ('sharedHeader', ?)
        ON CONFLICT(key) DO UPDATE SET val = excluded.val
        """, (json.dumps(header_data, ensure_ascii=False),))
    conn.close()
