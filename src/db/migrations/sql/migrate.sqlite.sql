
CREATE TABLE 'user' (
    email VARCHAR(255) NOT NULL, 
    username VARCHAR(24) NOT NULL, 
    password VARCHAR(255) NOT NULL, 
    is_admin BOOLEAN NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email),
    UNIQUE (username)
    CHECK (is_admin IN (0, 1))
);

CREATE TABLE language (
    iso_code VARCHAR(120) NOT NULL, 
    name VARCHAR NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (iso_code)
);

CREATE TABLE lexeme (
    lemma VARCHAR NOT NULL, 
    gloss VARCHAR, 
    subscript INTEGER, 
    language_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    UNIQUE (lemma, gloss, language_id)
);

CREATE TABLE word (
    form VARCHAR NOT NULL, 
    parsing VARCHAR(255), 
    gloss VARCHAR, 
    lexeme_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(lexeme_id) REFERENCES lexeme (id) 
);

CREATE TABLE collection (
    long_title VARCHAR, 
    title VARCHAR(255) NOT NULL, 
    author VARCHAR, 
    'order' INTEGER, 
    language_id INTEGER NOT NULL, 
    parent_id INTEGER, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    FOREIGN KEY(parent_id) REFERENCES collection (id) 
);

CREATE TABLE document (
    long_title VARCHAR, 
    title VARCHAR(255) NOT NULL, 
    author VARCHAR, 
    'order' INTEGER NOT NULL, 
    file_url VARCHAR NOT NULL, 
    collection_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(collection_id) REFERENCES collection (id),  
    UNIQUE (file_url) 
);

CREATE TABLE token (
    identifier VARCHAR(80) NOT NULL, 
    form VARCHAR NOT NULL, 
    gloss VARCHAR, 
    document_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(document_id) REFERENCES document (id), 
    UNIQUE (identifier, document_id)
);

CREATE TABLE token_words (
    token_id INTEGER NOT NULL, 
    word_id INTEGER NOT NULL, 
    FOREIGN KEY(token_id) REFERENCES token (id), 
    FOREIGN KEY(word_id) REFERENCES word (id) 
);
