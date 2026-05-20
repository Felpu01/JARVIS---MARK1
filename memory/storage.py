import json
from memory.supabase_client import supabase

TABLE = "mark34_memory"

# =========================
# LOAD ALL MEMORY
# =========================
def load_state():
    try:
        res = supabase.table(TABLE).select("*").execute()

        state = {
            "history": [],
            "tasks": [],
            "last_active": 0
        }

        for row in res.data:
            key = row["key"]
            value = row["value"]

            if key not in state:
                state[key] = []

            if isinstance(state[key], list):
                state[key].append(value)
            else:
                state[key] = value

        return state

    except Exception as e:
        print("⚠️ Supabase load error:", e)
        return {
            "history": [],
            "tasks": [],
            "last_active": 0
        }

# =========================
# SAVE SINGLE EVENT
# =========================
def save_state(key, value):
    try:
        supabase.table(TABLE).insert({
            "key": key,
            "value": value
        }).execute()

    except Exception as e:
        print("⚠️ Supabase save error:", e)
