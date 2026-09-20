import json
import sqlite3
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "researchpilot.db"


def get_connection():
    """
    创建 SQLite 数据库连接。
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_database():
    """
    创建项目、论文和 AI 分析结果所需的数据表。
    """

    connection = get_connection()

    try:

        connection.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                pages INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY (project_id)
                    REFERENCES projects(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS ai_analyses (
                project_id INTEGER PRIMARY KEY,
                analysis_json TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id)
                    REFERENCES projects(id)
                    ON DELETE CASCADE
            );
        """)

        connection.commit()

    finally:

        connection.close()

def save_project(project_name, papers, analysis):
    """
    保存一个项目、其中的论文，以及 AI 分析结果。

    如果项目名称已经存在，则更新原项目。
    """

    project_name = project_name.strip()

    if not project_name:
        raise ValueError("项目名称不能为空。")

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO projects (name)
            VALUES (?)
            ON CONFLICT(name)
            DO UPDATE SET
                updated_at = CURRENT_TIMESTAMP
            """,
            (project_name,)
        )

        project_row = connection.execute(
            """
            SELECT id
            FROM projects
            WHERE name = ?
            """,
            (project_name,)
        ).fetchone()

        project_id = project_row[0]

        connection.execute(
            """
            DELETE FROM papers
            WHERE project_id = ?
            """,
            (project_id,)
        )

        for paper in papers:

            connection.execute(
                """
                INSERT INTO papers (
                    project_id,
                    title,
                    pages,
                    text
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    project_id,
                    paper["title"],
                    paper["pages"],
                    paper["text"]
                )
            )

        if analysis:

            analysis_json = json.dumps(
                analysis,
                ensure_ascii=False
            )

            connection.execute(
                """
                INSERT INTO ai_analyses (
                    project_id,
                    analysis_json
                )
                VALUES (?, ?)
                ON CONFLICT(project_id)
                DO UPDATE SET
                    analysis_json = excluded.analysis_json,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    project_id,
                    analysis_json
                )
            )

        else:

            connection.execute(
                """
                DELETE FROM ai_analyses
                WHERE project_id = ?
                """,
                (project_id,)
            )

        connection.commit()

        return project_id

    finally:

        connection.close()
def list_projects():
    """
    返回所有已保存项目，按最近更新时间排序。
    """

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT id, name, updated_at
            FROM projects
            ORDER BY updated_at DESC
            """
        ).fetchall()

        projects = []

        for row in rows:
            projects.append({
                "id": row[0],
                "name": row[1],
                "updated_at": row[2]
            })

        return projects

    finally:

        connection.close()


def load_project(project_id):
    """
    根据项目编号读取项目、论文和 AI 分析结果。
    """

    connection = get_connection()

    try:

        project_row = connection.execute(
            """
            SELECT id, name
            FROM projects
            WHERE id = ?
            """,
            (project_id,)
        ).fetchone()

        if not project_row:
            return None

        paper_rows = connection.execute(
            """
            SELECT title, pages, text
            FROM papers
            WHERE project_id = ?
            """,
            (project_id,)
        ).fetchall()

        papers = []

        for row in paper_rows:
            papers.append({
                "title": row[0],
                "filename": row[0],
                "pages": row[1],
                "text": row[2]
            })

        analysis_row = connection.execute(
            """
            SELECT analysis_json
            FROM ai_analyses
            WHERE project_id = ?
            """,
            (project_id,)
        ).fetchone()

        analysis = None

        if analysis_row:
            analysis = json.loads(
                analysis_row[0]
            )

        return {
            "id": project_row[0],
            "name": project_row[1],
            "papers": papers,
            "analysis": analysis
        }

    finally:

        connection.close()

initialize_database()