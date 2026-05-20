import os

# =========================
# SYSTEM CONFIG
# =========================

SYSTEM_NAME = "MARK34"
VERSION = "1.0"

# =========================
# SUPABASE (desde Render env vars)
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# =========================
# MEMORY SETTINGS
# =========================
MAX_HISTORY = 100
MAX_TASKS = 50

# =========================
# AUTONOMY SETTINGS
# =========================
INACTIVITY_LIMIT = 60  # seconds
CLEANUP_INTERVAL = 10
