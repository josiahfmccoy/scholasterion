
CREATE TABLE language (
    iso_code VARCHAR(120) NOT NULL, 
    name VARCHAR NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (iso_code)
);

CREATE TABLE lexeme (
    lemma VARCHAR NOT NULL, 
    language_id INTEGER NOT NULL,  
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(language_id) REFERENCES language (id), 
    UNIQUE (lemma, language_id)
);

CREATE TABLE word (
    form VARCHAR NOT NULL, 
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
    name VARCHAR NOT NULL, 
    file_url VARCHAR NOT NULL,  
    text_id INTEGER NOT NULL, 
    id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(text_id) REFERENCES 'text' (id), 
    UNIQUE (file_url)
    UNIQUE (name, text_id)
);
