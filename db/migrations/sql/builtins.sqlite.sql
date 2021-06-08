DELETE FROM token_words;
DELETE FROM token;
--DELETE FROM word;
--DELETE FROM lexeme;
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

INSERT INTO volume (text_id, 'order', name, file_url) VALUES
(1, 1, 'Book I: Laypeople', 'apostolic-constitutions/book-1.xml'),
(1, 2, 'Book II: Bishops, Elders, and Deacons', 'apostolic-constitutions-2.xml'),
(1, 3, 'Book III: Widows', 'apostolic-constitutions/book-3.xml'),
(1, 4, 'Book IV: Orphans', 'apostolic-constitutions/book-4.xml'),
(2, 1, 'Book I', 'antiquities-of-the-jews/book-1.xml'),
(2, 2, 'Book II', 'antiquities-of-the-jews/book-2.xml'),
(2, 3, 'Book III', 'antiquities-of-the-jews/book-3.xml'),
(2, 4, 'Book IV', 'antiquities-of-the-jews/book-4.xml'),
(2, 5, 'Book V', 'antiquities-of-the-jews/book-5.xml'),
(2, 6, 'Book VI', 'antiquities-of-the-jews/book-6.xml'),
(2, 7, 'Book VII', 'antiquities-of-the-jews/book-7.xml'),
(2, 8, 'Book VIII', 'antiquities-of-the-jews/book-8.xml'),
(2, 9, 'Book IX', 'antiquities-of-the-jews/book-9.xml'),
(2, 10, 'Book X', 'antiquities-of-the-jews/book-10.xml'),
(2, 11, 'Book XI', 'antiquities-of-the-jews/book-11.xml'),
(2, 12, 'Book XII', 'antiquities-of-the-jews/book-12.xml'),
(2, 13, 'Book XIII', 'antiquities-of-the-jews/book-13.xml'),
(2, 14, 'Book XIV', 'antiquities-of-the-jews/book-14.xml'),
(2, 15, 'Book XV', 'antiquities-of-the-jews/book-15.xml'),
(2, 16, 'Book XVI', 'antiquities-of-the-jews/book-16.xml'),
(2, 17, 'Book XVII', 'antiquities-of-the-jews/book-17.xml'),
(2, 18, 'Book XVIII', 'antiquities-of-the-jews/book-18.xml'),
(2, 19, 'Book XVIX', 'antiquities-of-the-jews/book-19.xml'),
(2, 20, 'Book XX', 'antiquities-of-the-jews/book-20.xml'),
(3, 1, 'Book I', 'consolation-of-philosophy.xml'),
(4, 1, 'Book I', 'apology-to-autolycus/book-1.xml'),
(4, 2, 'Book II', 'apology-to-autolycus/book-2.xml'),
(4, 3, 'Book III', 'apology-to-autolycus/book-3.xml');
