"""E-Rapor Pondok Pesantren - SIAKAD Modern Full Stack Flask + SQLite Application
Madrasah Islami Salafi Ihya 'Ulumiddin Pamarican
Multi-Kelas (Kelas 1 s.d. 6 MISIU), Multi-Wali Kelas, 63 Santri di Kelas 2,
Bulk Spreadsheet Input, Auto Arabic & Indonesian Conversions, Logo Customization.
"""

import json
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import db

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "ihya-ulumiddin-modern-siakad-2026-secret")

UPLOAD_FOLDER = os.path.join(app.root_path, "static")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure database is initialized
db.init_db()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/Ihya 'Ulumiddin.png")
@app.route("/Ihya%20'Ulumiddin.png")
@app.route("/Ihya%20%27Ulumiddin.png")
def serve_root_logo():
    return send_from_directory(app.root_path, "Ihya 'Ulumiddin.png")


@app.route("/")
def index():
    user = session.get("user")
    class_id = request.args.get("class_id")
    if user:
        if user.get("role") == "wali":
            class_id = user.get("classId")
        elif user.get("role") == "santri":
            class_id = user.get("classId")
    state = db.get_full_state(class_id, user=user)
    return render_template("index.html", initial_state=state, current_user=user)


@app.route("/api/state", methods=["GET"])
def api_state():
    user = session.get("user")
    class_id = request.args.get("class_id")
    if user:
        if user.get("role") == "wali":
            class_id = user.get("classId")
        elif user.get("role") == "santri":
            class_id = user.get("classId")
    return jsonify(db.get_full_state(class_id, user=user))


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = db.authenticate_user(username, password)
    if user:
        session["user"] = user
        # If wali kelas, set active class in meta
        if user["role"] == "wali" and user.get("classId"):
            db.save_active_class(user["classId"])
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Username / NIS atau kata sandi salah. Silakan periksa kembali."}), 401


@app.route("/api/logout", methods=["POST", "GET"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/current-user", methods=["GET"])
def api_current_user():
    return jsonify({"user": session.get("user")})


@app.route("/api/select-class", methods=["POST"])
def api_select_class():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "ustadz"]:
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin atau Ustadz lintas kelas yang berhak memilih kelas."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")

    if user.get("role") == "ustadz":
        assigned_classes = {a["class_id"] for a in (user.get("assignments") or [])}
        if class_id not in assigned_classes:
            return jsonify({"success": False, "message": "Akses ditolak. Anda tidak mengampu mata pelajaran di kelas ini."}), 403
        return jsonify({"success": True, "state": db.get_full_state(class_id, user=user)})

    db.save_active_class(class_id)
    return jsonify({"success": True, "state": db.get_full_state(class_id, user=user)})


@app.route("/api/ustadz/save-subject-scores", methods=["POST"])
def api_ustadz_save_subject_scores():
    """Save or upload grades for a single subject taught by an Ustadz/Ustadzah (or Wali Kelas / Admin)."""
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali", "ustadz"]:
        return jsonify({"success": False, "message": "Akses ditolak. Silakan login sebagai Ustadz, Wali Kelas, atau Admin."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    sem_key = data.get("semKey", "sem1")
    subject_category = data.get("subjectCategory", "tulis")
    try:
        subject_index = int(data.get("subjectIndex", 0))
    except Exception:
        return jsonify({"success": False, "message": "Indeks mata pelajaran tidak valid."}), 400
    scores = data.get("scores", [])

    if not scores:
        return jsonify({"success": False, "message": "Tidak ada data nilai yang dikirim."}), 400

    allowed_jk = "ALL"
    if user.get("role") == "wali":
        if class_id != user.get("classId"):
            return jsonify({"success": False, "message": "Akses ditolak. Wali Kelas hanya berhak menginput nilai di kelasnya sendiri."}), 403
    elif user.get("role") == "ustadz":
        assignments = user.get("assignments") or []
        matching = [
            a for a in assignments
            if a["class_id"] == class_id
            and a["subject_category"] == subject_category
            and int(a["subject_index"]) == subject_index
        ]
        if not matching:
            return jsonify({
                "success": False,
                "message": "Akses ditolak! Anda tidak terdaftar sebagai pengampu mata pelajaran ini pada Jadwal Pengajian Resmi."
            }), 403
        # Check if teacher is assigned to ALL, L, or P
        jk_set = {m.get("jk_filter", "ALL") for m in matching}
        if "ALL" in jk_set or ("L" in jk_set and "P" in jk_set):
            allowed_jk = "ALL"
        elif "L" in jk_set:
            allowed_jk = "L"
        elif "P" in jk_set:
            allowed_jk = "P"

    try:
        updated = db.save_subject_scores(
            class_id=class_id,
            sem_key=sem_key,
            subject_category=subject_category,
            subject_index=subject_index,
            scores=scores,
            allowed_jk=allowed_jk
        )
        return jsonify({"success": True, "updated": updated, "allowedJk": allowed_jk})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal menyimpan nilai mata pelajaran: {str(e)}"}), 400


@app.route("/api/active_semester", methods=["POST"])
def api_active_semester():
    data = request.get_json(silent=True) or {}
    active_sem = data.get("activeSemester", "sem1")
    db.save_active_semester(active_sem)
    return jsonify({"success": True})


@app.route("/api/student-progression/<int:student_id>", methods=["GET"])
def api_student_progression(student_id):
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "message": "Silakan login terlebih dahulu."}), 401
    if user.get("role") == "santri" and user.get("studentId") != student_id:
        return jsonify({"success": False, "message": "Akses ditolak. Anda hanya berhak melihat grafik milik Anda sendiri."}), 403
    progression = db.get_student_progression(student_id)
    return jsonify({"success": True, "progression": progression})


@app.route("/api/student/save", methods=["POST"])
def api_student_save():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak. Santri tidak berhak menginput nilai."}), 403

    data = request.get_json(silent=True) or {}
    sid = data.get("id")
    if not sid:
        return jsonify({"success": False, "message": "ID santri tidak valid."}), 400

    if user.get("role") == "wali":
        st = db.get_student_by_id(int(sid))
        if not st or st["class_id"] != user.get("classId"):
            return jsonify({"success": False, "message": "Akses ditolak. Anda hanya berhak mengedit santri di kelas Anda."}), 403

    db.save_single_student_scores(data)
    return jsonify({"success": True})


@app.route("/api/student/bulk-save", methods=["POST"])
def api_student_bulk_save():
    """Bulk save all student scores for an entire class at once."""
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak. Santri tidak berhak menginput nilai."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    if user.get("role") == "wali" and class_id != user.get("classId"):
        return jsonify({"success": False, "message": "Akses ditolak. Anda hanya berhak menginput nilai kelas Anda sendiri."}), 403

    sem_key = data.get("semKey", "sem1")
    students = data.get("students", [])

    if not students:
        return jsonify({"success": False, "message": "Tidak ada data santri yang dikirim."}), 400

    db.save_bulk_scores(class_id, sem_key, students)
    return jsonify({"success": True, "count": len(students)})


@app.route("/api/student/add", methods=["POST"])
def api_student_add():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    if user.get("role") == "wali" and class_id != user.get("classId"):
        return jsonify({"success": False, "message": "Akses ditolak. Anda hanya dapat menambah santri di kelas Anda."}), 403

    nis = data.get("nis", "").strip()
    nama = data.get("nama", "").strip()

    if not nis or not nama:
        return jsonify({"success": False, "message": "NIS dan Nama santri wajib diisi."}), 400

    try:
        new_id = db.add_student(
            class_id=class_id,
            nis=nis,
            nama=nama,
            jk=data.get("jk", "L"),
            wali=data.get("wali", ""),
            ttl=data.get("ttl", ""),
            agama=data.get("agama", "Islam"),
            anak_ke=data.get("anak_ke", ""),
            status_keluarga=data.get("status_keluarga", "Anak Kandung"),
            alamat=data.get("alamat", ""),
            diterima_kelas=data.get("diterima_kelas", ""),
            diterima_tanggal=data.get("diterima_tanggal", ""),
            sekolah_asal=data.get("sekolah_asal", ""),
            sekolah_asal_alamat=data.get("sekolah_asal_alamat", ""),
            ayah_nama=data.get("ayah_nama", ""),
            ibu_nama=data.get("ibu_nama", ""),
            ortu_alamat=data.get("ortu_alamat", ""),
            no_hp=data.get("no_hp", ""),
            ayah_pekerjaan=data.get("ayah_pekerjaan", ""),
            ibu_pekerjaan=data.get("ibu_pekerjaan", "")
        )
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal menambah santri (NIS mungkin sudah terdaftar): {str(e)}"}), 400


@app.route("/api/student/update", methods=["POST"])
def api_student_update():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak."}), 403

    data = request.get_json(silent=True) or {}
    sid = data.get("id")
    if not sid:
        return jsonify({"success": False, "message": "Data tidak lengkap."}), 400

    if user.get("role") == "wali":
        st = db.get_student_by_id(int(sid))
        if not st or st["class_id"] != user.get("classId"):
            return jsonify({"success": False, "message": "Akses ditolak. Anda hanya dapat mengedit santri di kelas Anda."}), 403

    nis = data.get("nis", "").strip()
    nama = data.get("nama", "").strip()

    if not nis or not nama:
        return jsonify({"success": False, "message": "NIS dan Nama santri wajib diisi."}), 400

    try:
        db.update_student(
            student_id=int(sid),
            nis=nis,
            nama=nama,
            jk=data.get("jk", "L"),
            wali=data.get("wali", ""),
            ttl=data.get("ttl", ""),
            agama=data.get("agama", "Islam"),
            anak_ke=data.get("anak_ke", ""),
            status_keluarga=data.get("status_keluarga", "Anak Kandung"),
            alamat=data.get("alamat", ""),
            diterima_kelas=data.get("diterima_kelas", ""),
            diterima_tanggal=data.get("diterima_tanggal", ""),
            sekolah_asal=data.get("sekolah_asal", ""),
            sekolah_asal_alamat=data.get("sekolah_asal_alamat", ""),
            ayah_nama=data.get("ayah_nama", ""),
            ibu_nama=data.get("ibu_nama", ""),
            ortu_alamat=data.get("ortu_alamat", ""),
            no_hp=data.get("no_hp", ""),
            ayah_pekerjaan=data.get("ayah_pekerjaan", ""),
            ibu_pekerjaan=data.get("ibu_pekerjaan", "")
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal memperbarui data: {str(e)}"}), 400


@app.route("/api/student/delete", methods=["POST"])
def api_student_delete():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak."}), 403

    data = request.get_json(silent=True) or {}
    sid = data.get("id")
    if not sid:
        return jsonify({"success": False, "message": "ID santri tidak valid."}), 400

    if user.get("role") == "wali":
        st = db.get_student_by_id(int(sid))
        if not st or st["class_id"] != user.get("classId"):
            return jsonify({"success": False, "message": "Akses ditolak. Anda hanya dapat menghapus santri di kelas Anda."}), 403

    db.delete_student(int(sid))
    return jsonify({"success": True})


@app.route("/api/student/import", methods=["POST"])
def api_student_import():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    if user.get("role") == "wali" and class_id != user.get("classId"):
        return jsonify({"success": False, "message": "Akses ditolak. Anda hanya dapat mengimpor santri ke kelas Anda."}), 403

    rows = data.get("rows", [])
    if not rows:
        return jsonify({"success": False, "message": "Tidak ada baris data yang diimpor."}), 400

    success_count, errors = db.import_students(class_id, rows)
    return jsonify({"success": True, "imported": success_count, "errors": errors})


@app.route("/api/config/save", methods=["POST"])
def api_config_save():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak mengubah pengaturan madrasah."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    sem_key = data.get("semKey", "sem1")
    db.save_class_config(class_id, sem_key, data)
    return jsonify({"success": True})


@app.route("/api/subjects/save", methods=["POST"])
def api_subjects_save():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak mengubah daftar mapel kitab."}), 403

    data = request.get_json(silent=True) or {}
    class_id = data.get("classId", "kls2")
    sem_key = data.get("semKey", "sem1")
    subjects = data.get("subjects", {})
    db.save_subjects(class_id, sem_key, subjects)
    return jsonify({"success": True})


@app.route("/api/subjects/template/<class_id>", methods=["GET"])
def api_subjects_template(class_id):
    template = db.get_class_curriculum_template(class_id)
    return jsonify({"success": True, "template": template})


@app.route("/api/upload-logo", methods=["POST"])
def api_upload_logo():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak mengganti logo madrasah."}), 403

    if "logo" not in request.files:
        return jsonify({"success": False, "message": "Tidak ada file yang diunggah."}), 400

    file = request.files["logo"]
    if file.filename == "":
        return jsonify({"success": False, "message": "Nama file kosong."}), 400

    if file and allowed_file(file.filename):
        filename = "logo-madrasah.png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        jpg_path = os.path.join(app.config["UPLOAD_FOLDER"], "logo-madrasah.jpg")
        try:
            import shutil
            shutil.copyfile(filepath, jpg_path)
        except Exception:
            pass

        logo_url = "/static/logo-madrasah.png?v=" + str(int(os.path.getmtime(filepath)))
        db.update_logo_url(logo_url)
        return jsonify({"success": True, "logoUrl": logo_url})

    return jsonify({"success": False, "message": "Tipe file tidak didukung (gunakan PNG, JPG, atau WebP)."}), 400


@app.route("/api/change-password", methods=["POST"])
def api_change_password():
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "message": "Silakan login terlebih dahulu."}), 401

    data = request.get_json(silent=True) or {}
    old_pw = data.get("oldPassword", "").strip()
    new_pw = data.get("newPassword", "").strip()

    if not old_pw or not new_pw:
        return jsonify({"success": False, "message": "Password lama dan password baru wajib diisi."}), 400

    success, msg = db.update_user_password(user["id"], old_pw, new_pw)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 400


@app.route("/api/admin/accounts", methods=["GET"])
def api_admin_accounts():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak melihat daftar akun & password unik."}), 403

    accounts = db.get_all_accounts_for_admin()
    return jsonify({"success": True, "accounts": accounts})


@app.route("/api/admin/account/update-password", methods=["POST"])
def api_admin_update_account_password():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak mengubah password akun."}), 403

    data = request.get_json(silent=True) or {}
    target_user_id = data.get("userId")
    new_pw = data.get("newPassword", "").strip()
    if not target_user_id or not new_pw:
        return jsonify({"success": False, "message": "ID Akun dan Password baru wajib diisi."}), 400

    success, result = db.admin_update_user_password(target_user_id, new_pw)
    if success:
        return jsonify({
            "success": True,
            "newPassword": result,
            "accounts": db.get_all_accounts_for_admin()
        })
    return jsonify({"success": False, "message": result}), 400


@app.route("/api/admin/account/regenerate-passwords", methods=["POST"])
def api_admin_regenerate_passwords():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak men-generate ulang password unik."}), 403

    data = request.get_json(silent=True) or {}
    target_role = data.get("role", "ALL")
    class_id = data.get("classId")
    user_id = data.get("userId")

    success, count, last_pw = db.admin_regenerate_passwords(target_role=target_role, class_id=class_id, user_id=user_id)
    return jsonify({
        "success": success,
        "updatedCount": count,
        "lastPassword": last_pw,
        "accounts": db.get_all_accounts_for_admin()
    })


@app.route("/api/backup/export", methods=["GET"])
def api_backup_export():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak. Fitur backup hanya untuk Admin dan Wali Kelas."}), 403

    target_cid = None
    if user.get("role") == "wali":
        target_cid = user.get("classId")
    else:
        target_cid = request.args.get("class_id")

    backup_data = db.export_backup_data(target_cid)
    return jsonify({"success": True, "backup": backup_data})


@app.route("/api/backup/restore", methods=["POST"])
def api_backup_restore():
    user = session.get("user")
    if not user or user.get("role") not in ["admin", "wali"]:
        return jsonify({"success": False, "message": "Akses ditolak. Fitur restore hanya untuk Admin dan Wali Kelas."}), 403

    data = request.get_json(silent=True) or {}
    backup_payload = data.get("backup")
    if not backup_payload:
        return jsonify({"success": False, "message": "Data backup tidak ditemukan."}), 400

    success, msg = db.restore_backup_data(backup_payload, user=user)
    if success:
        return jsonify({"success": True, "message": msg, "state": db.get_full_state(user=user)})
    return jsonify({"success": False, "message": msg}), 400


@app.route("/api/reset", methods=["POST"])
def api_reset():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Akses ditolak. Hanya Super Admin yang berhak mereset database."}), 403

    db.seed_database()
    return jsonify({"success": True, "state": db.get_full_state(user=user)})


@app.route("/cetak/<int:student_id>")
def print_student_rapor(student_id):
    sem = request.args.get("sem", "sem1")
    state = db.get_full_state("kls2")
    student = next((s for s in state["students"] if s["id"] == student_id), None)
    if not student:
        # Search all classes if needed
        for c in state["classes"]:
            c_state = db.get_full_state(c["id"])
            st = next((s for s in c_state["students"] if s["id"] == student_id), None)
            if st:
                student = st
                state = c_state
                break
    if not student:
        return "Santri tidak ditemukan", 404
    return render_template("index.html", initial_state=state, current_user=session.get("user"), auto_print_student_id=student_id, auto_sem=sem)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
