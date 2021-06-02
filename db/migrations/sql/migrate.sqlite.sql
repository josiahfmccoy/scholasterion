
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
    language_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    UNIQUE (lemma, gloss, language_id)
);

CREATE TABLE word (
    form VARCHAR NOT NULL, 
    parsing VARCHAR(255), 
    lexeme_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(lexeme_id) REFERENCES lexeme (id) 
);

CREATE TABLE 'text' (
    name VARCHAR NOT NULL, 
    language_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    UNIQUE (name, language_id)
);

CREATE TABLE volume (
    order INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    file_url VARCHAR NOT NULL,  
    text_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(text_id) REFERENCES 'text' (id), 
    UNIQUE (file_url)
    UNIQUE (name, text_id)
);

CREATE TABLE token (
    identifier VARCHAR(80) NOT NULL, 
    form VARCHAR NOT NULL, 
    gloss VARCHAR, 
    volume_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(volume_id) REFERENCES volume (id), 
    UNIQUE (identifier, volume_id)
);

CREATE TABLE token_words (
    token_id INTEGER NOT NULL, 
    word_id INTEGER NOT NULL, 
    FOREIGN KEY(token_id) REFERENCES token (id), 
    FOREIGN KEY(word_id) REFERENCES word (id) 
);
