# Database Schema

The AI-Tender-System uses a hybrid storage architecture, combining a SQLite database for structured data and a FAISS index for high-performance vector search.

## Architecture

-   **SQLite**: Used to store metadata about documents, users, projects, and other relational data.
-   **FAISS**: Used to store and search vector embeddings of document content for semantic search.
-   **Filesystem**: Used to store the original uploaded document files.

## SQLite Schema

### Core Tables

#### `product_documents`

Stores information about each document in the knowledge base.

```sql
CREATE TABLE product_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    category ENUM('tech', 'impl', 'service', 'cases') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_size INTEGER,
    security_level ENUM('public', 'internal', 'confidential', 'secret') DEFAULT 'internal',
    status ENUM('processing', 'active', 'archived', 'error') DEFAULT 'processing',
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    description TEXT,
    -- ... and other metadata fields
);
```

#### `document_chunks`

Stores the chunked content of each document, which is used for vectorization.

```sql
CREATE TABLE document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_type ENUM('text', 'table', 'image', 'list') DEFAULT 'text',
    page_number INTEGER,
    vector_id INTEGER, -- Mapping to the FAISS index
    FOREIGN KEY (document_id) REFERENCES product_documents(id) ON DELETE CASCADE
);
```

### Supporting Tables

-   **`document_metadata`**: Stores additional key-value metadata for each document.
-   **`search_logs`**: Logs all search queries for analytics.
-   **`companies`**: Stores information about companies.
-   **`projects`**: Stores information about tender projects.

## FAISS Vector Index

The vector index is used for semantic search. It stores vector embeddings of the document chunks.

-   **Dimension**: 384 (from `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
-   **Index Type**: `IndexFlatIP` (Inner Product)
-   **Files**: The FAISS index is stored on the filesystem, typically in `data/vector_indexes/`. A mapping file (`id_mapping.json`) is used to map the FAISS vector IDs back to the `document_chunks` table.
