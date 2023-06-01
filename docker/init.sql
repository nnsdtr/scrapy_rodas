
/* DOCUMENTOS HTML */
-- Cria tabela
CREATE TABLE html_document (
    id                SERIAL     PRIMARY KEY,
    category          CHAR(10)   NOT NULL,
    url_hash          CHAR(32)   NOT NULL  UNIQUE,
    html_hash         CHAR(32)   NOT NULL,
    url               TEXT       NOT NULL,
    html              TEXT       NOT NULL,
    is_active         BOOLEAN    NOT NULL  DEFAULT TRUE,
    num_of_downloads  INTEGER    NOT NULL  DEFAULT 1,
    last_visit_on     TIMESTAMP  NOT NULL,
    first_visit_on    TIMESTAMP  NOT NULL
);

-- Cria índice para buscas via hash
CREATE UNIQUE INDEX idx_html_doc_url_hash  ON html_document USING btree (url_hash);
CREATE INDEX idx_html_doc_html_hash ON html_document USING btree (html_hash);
CREATE INDEX idx_html_doc_category  ON html_document USING btree (category);

-- Cria uma função para atualizar campos de timestamp em updates
CREATE  FUNCTION update_timestamp_html_doc()
RETURNS TRIGGER AS $$
BEGIN
    NEW.num_of_downloads = NEW.num_of_downloads + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Cria trigger para atualizar campos de timestamp em updates
CREATE TRIGGER update_timestamp_html_doc
    BEFORE UPDATE ON html_document
    FOR EACH ROW
        EXECUTE PROCEDURE update_timestamp_html_doc();


/* LOG para falhas de download */
-- Cria tabela
CREATE TABLE failed_download_log (
    id            SERIAL     PRIMARY KEY,
    url_hash      CHAR(32)   NOT NULL  UNIQUE,
    url           TEXT       NOT NULL,
    last_status   SMALLINT   NOT NULL,
    num_of_fails  INTEGER    NOT NULL  DEFAULT 1,
    last_fail_on  TIMESTAMP  NOT NULL,
    first_fail_on TIMESTAMP  NOT NULL
);
-- Cria índice para buscas de documentos via hash
CREATE UNIQUE INDEX idx_failed_url_hash ON failed_download_log USING btree (url_hash);

-- Cria função para atualizar campos de timestamp em updates
CREATE  FUNCTION update_timestamp_failed()
RETURNS TRIGGER AS $$
BEGIN
    NEW.num_of_fails = NEW.num_of_fails + 1;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Cria trigger para atualizar campos de timestamp em updates
CREATE TRIGGER update_timestamp_failed
    BEFORE UPDATE ON failed_download_log
    FOR EACH ROW
        EXECUTE PROCEDURE update_timestamp_failed();
