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


def resolve_upload_directory(root, subfolder):
    """Prevent traversal outside the configured upload root."""
    if not isinstance(subfolder, str) or not subfolder.strip():
        raise ValueError("Upload subfolder is required")
    if "\x00" in subfolder:
        raise ValueError("Invalid upload subfolder")
    base = Path(root).resolve()
    candidate = (base / subfolder).resolve()
    if not candidate.is_relative_to(base) or candidate == base:
        raise ValueError("Upload directory must stay inside configured root")
    return candidate


def save_upload(file_storage, subfolder):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type.")

    if "\x00" in file_storage.filename:
        raise ValueError("Invalid filename")
    original = secure_filename(file_storage.filename)
    if not original or "." not in original:
        raise ValueError("Invalid filename")
    extension = original.rsplit(".", 1)[1].lower()
    stored = f"{uuid4().hex}.{extension}"
    target_dir = resolve_upload_directory(current_app.config["UPLOAD_FOLDER"], subfolder)
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / stored
    file_storage.save(path)
    return original, stored, str(path), extension


def verify_hmac_signature(raw_body, signature, secret):
    if not isinstance(raw_body, bytes) or not isinstance(signature, str) or not isinstance(secret, str):
        return False
    if not signature or not secret:
        return False
    if len(signature) != 64 or any(char not in "0123456789abcdefABCDEF" for char in signature):
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
