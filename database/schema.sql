CREATE DATABASE IF NOT EXISTS pdf_parser;

USE pdf_parser;

-- =====================================================
-- Table: pdfs
-- Stores information about uploaded PDF files
-- =====================================================

CREATE TABLE IF NOT EXISTS pdfs (

    pdf_id INT AUTO_INCREMENT PRIMARY KEY,

    filename VARCHAR(255) NOT NULL,

    stored_filename VARCHAR(255) NOT NULL,

    file_path VARCHAR(500) NOT NULL,

    file_size BIGINT NOT NULL,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =====================================================
-- Table: pdf_metadata
-- Stores extracted resume information
-- =====================================================

CREATE TABLE IF NOT EXISTS pdf_metadata (

    metadata_id INT AUTO_INCREMENT PRIMARY KEY,

    pdf_id INT NOT NULL,

    full_name VARCHAR(255),

    email VARCHAR(255),

    phone_number VARCHAR(30),

    linkedin VARCHAR(500),

    github VARCHAR(500),

    summary TEXT,

    skills JSON,

    education JSON,

    experience JSON,

    projects JSON,

    certifications JSON,

    languages JSON,

    FOREIGN KEY (pdf_id)
        REFERENCES pdfs(pdf_id)
        ON DELETE CASCADE

);