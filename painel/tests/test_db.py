from painel.appdata import appdata_dir
from painel.db import db_path, get_connection


def test_db_path_lives_under_isolated_appdata(isolated_appdata):
    assert db_path().parent == appdata_dir()
    assert str(db_path()).startswith(str(isolated_appdata))


def test_get_connection_creates_schema():
    conn = get_connection()
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    assert {"workspaces", "jobs"} <= tables
    conn.close()


def test_jobs_table_insert_and_read():
    conn = get_connection()
    conn.execute(
        "INSERT INTO jobs (workspace_path, slug, harness, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("/tmp/ws", "meu-slug", "echo", "pending", "2026-08-13T00:00:00", "2026-08-13T00:00:00"),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM jobs WHERE slug = ?", ("meu-slug",)).fetchone()
    assert row["harness"] == "echo"
    assert row["status"] == "pending"
    conn.close()
