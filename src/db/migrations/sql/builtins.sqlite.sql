DELETE FROM token_words;
DELETE FROM token;
DELETE FROM word;
DELETE FROM lexeme;
DELETE FROM document;
DELETE FROM language;

INSERT INTO language (id, name, iso_code) VALUES
(1, 'Ancient Greek', 'grc'),
(2, 'Latin', 'lat')
;

INSERT INTO document (
    id, title, author, language_id,
    file_url
) VALUES
(
    1, 'Commentaries', 'Eusebius of Caesarea', 1,
    'eusebius-commentaries.zip'
),
(
    2, 'History of the Church', 'Eusebius of Caesarea', 1,
    'ecclesiastical-history.zip'
),
(
    3, 'Dialogues', 'Lucian of Samosata', 1,
    'lucian-dialogues.zip'
),
(
    4, 'Sayings of the Desert Fathers', 'Anonymous', 1,
    'sayings-of-the-desert-fathers.zip'
)
;
