DELETE FROM word;
DELETE FROM lexeme;
DELETE FROM volume;
DELETE FROM 'text';
DELETE FROM language;

INSERT INTO language (id, name, iso_code) VALUES
(1, 'Ancient Greek', 'grc'),
(2, 'Latin', 'lat');

INSERT INTO 'text' (id, name, language_id) VALUES
(1, 'Apostolic Constitutions', 1),
(2, 'Antiquities of the Jews', 1),
(3, 'Consolation of Philosophy', 2),
(4, 'Apology to Autolycus', 1);

INSERT INTO volume (text_id, order, name, file_url) VALUES
(1, 1, 'Book I: Laypeople', 'apostolic-constitutions-1.xml'),
(1, 2, 'Book II: Bishops, Elders, and Deacons', 'apostolic-constitutions-2.xml'),
(1, 3, 'Book III: Widows', 'apostolic-constitutions-3.xml'),
(1, 4, 'Book IV: Orphans', 'apostolic-constitutions-4.xml'),
(2, 1, 'Book I', 'antiquities-of-the-jews-1.xml'),
(3, 1, 'Book I', 'consolation-of-philosophy.xml'),
(4, 1, 'Book I', 'apology-to-autolycus-1.xml'),
(4, 2, 'Book II', 'apology-to-autolycus-2.xml'),
(4, 3, 'Book III', 'apology-to-autolycus-3.xml');
