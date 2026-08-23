import json

from database.connection import get_connection


def save_resume(
    filename,
    stored_filename,
    file_path,
    file_size,
    metadata,
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        pdf_query = """
        INSERT INTO pdfs
        (
            filename,
            stored_filename,
            file_path,
            file_size
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            pdf_query,
            (
                filename,
                stored_filename,
                file_path,
                file_size,
            ),
        )

        pdf_id = cursor.lastrowid

        metadata_query = """
        INSERT INTO pdf_metadata
        (
            pdf_id,
            full_name,
            email,
            phone_number,
            linkedin,
            github,
            summary,
            skills,
            education,
            experience,
            projects,
            certifications,
            languages
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        cursor.execute(
            metadata_query,
            (
                pdf_id,
                metadata.get("full_name"),
                metadata.get("email"),
                metadata.get("phone_number"),
                metadata.get("linkedin"),
                metadata.get("github"),
                metadata.get("summary"),
                json.dumps(metadata.get("skills")),
                json.dumps(metadata.get("education")),
                json.dumps(metadata.get("experience")),
                json.dumps(metadata.get("projects")),
                json.dumps(metadata.get("certifications")),
                json.dumps(metadata.get("languages")),
            ),
        )

        connection.commit()
        return pdf_id

    finally:
        cursor.close()
        connection.close()


def get_all_resumes():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            p.pdf_id,
            p.filename,
            p.stored_filename,
            p.file_path,
            p.file_size,
            p.uploaded_at,
            m.full_name,
            m.email,
            m.phone_number,
            m.linkedin,
            m.github,
            m.summary,
            m.skills,
            m.education,
            m.experience,
            m.projects,
            m.certifications,
            m.languages
        FROM pdfs AS p
        INNER JOIN pdf_metadata AS m
            ON p.pdf_id = m.pdf_id
        ORDER BY p.pdf_id DESC
        """

        cursor.execute(query)

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()


def get_resume(pdf_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            p.pdf_id,
            p.filename,
            p.stored_filename,
            p.file_path,
            p.file_size,
            p.uploaded_at,
            m.full_name,
            m.email,
            m.phone_number,
            m.linkedin,
            m.github,
            m.summary,
            m.skills,
            m.education,
            m.experience,
            m.projects,
            m.certifications,
            m.languages
        FROM pdfs AS p
        INNER JOIN pdf_metadata AS m
            ON p.pdf_id = m.pdf_id
        WHERE p.pdf_id = %s
        """

        cursor.execute(query, (pdf_id,))
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()


def update_resume(
    pdf_id,
    metadata,
):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        UPDATE pdf_metadata
        SET
            full_name = %s,
            email = %s,
            phone_number = %s,
            linkedin = %s,
            github = %s,
            summary = %s,
            skills = %s,
            education = %s,
            experience = %s,
            projects = %s,
            certifications = %s,
            languages = %s
        WHERE pdf_id = %s
        """

        cursor.execute(
            query,
            (
                metadata.get("full_name"),
                metadata.get("email"),
                metadata.get("phone_number"),
                metadata.get("linkedin"),
                metadata.get("github"),
                metadata.get("summary"),
                json.dumps(metadata.get("skills")),
                json.dumps(metadata.get("education")),
                json.dumps(metadata.get("experience")),
                json.dumps(metadata.get("projects")),
                json.dumps(metadata.get("certifications")),
                json.dumps(metadata.get("languages")),
                pdf_id,
            ),
        )

        connection.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        connection.close()


def delete_resume(pdf_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        query = """
        DELETE FROM pdfs
        WHERE pdf_id = %s
        """

        cursor.execute(query, (pdf_id,))

        connection.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        connection.close()