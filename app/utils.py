import hmac
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename


ORDER_STATUSES = [
    "pending",
    "under_review",
    "in_progress",
    "waiting_documents",
    "completed",
    "rejected",
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage, subfolder):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type.")

    original = secure_filename(file_storage.filename)
    extension = original.rsplit(".", 1)[1].lower()
    stored = f"{uuid4().hex}.{extension}"
    target_dir = Path(current_app.config["UPLOAD_FOLDER"]) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / stored
    file_storage.save(path)
    return original, stored, str(path), extension


def verify_hmac_signature(raw_body, signature, secret):
    if not signature or not secret:
        return False
    digest = hmac.new(secret.encode("utf-8"), raw_body, sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


def audit(db, AuditLog, actor, action, entity_type=None, entity_id=None, metadata=None):
    db.session.add(
        AuditLog(
            actor_id=getattr(actor, "id", None),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            meta=metadata or {},
        )
    )
