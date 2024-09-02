DROP DATABASE IF EXISTS bellicious;
CREATE DATABASE bellicious;
USE bellicious;
CREATE TABLE user(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) UNIQUE NOT NULL, email VARCHAR(150) UNIQUE NOT NULL, password VARCHAR(256) NOT NULL, security varchar(1000) type INT DEFAULT 1, security varchar(1000), date_created DATETIME DEFAULT CURRENT_TIMESTAMP, confirmed INT DEFAULT 0, CHARACTER SET utf8 COLLATE utf8_general_ci);
CREATE TABLE BOOKMARK(id INT AUTO_INCREMENT PRIMARY KEY, url VARCHAR(2047) NOT NULL, annotation varchar(500), title VARCHAR(100) NOT NULL, description varchar(2000), likes INT DEFAULT 0, type INT DEFAULT 0, date_created DATETIME DEFAULT CURRENT_TIMESTAMP, id_user INT, FOREIGN KEY (id_user) REFERENCES user(id) ON DELETE CASCADE) CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE TABLE tag(id INT AUTO_INCREMENT PRIMARY KEY, tag varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci);
CREATE TABLE bookmark_tag(id_bookmark int, id_tag int, PRIMARY KEY(id_bookmark, id_tag), FOREIGN KEY(id_bookmark) REFERENCES bookmark(id) ON DELETE CASCADE, FOREIGN KEY(id_tag) REFERENCES tag(id) ON DELETE CASCADE) CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE TABLE feedback(id INT AUTO_INCREMENT PRIMARY KEY, text VARCHAR(200), id_user INT, FOREIGN KEY(id_user) REFERENCES user(id) ON DELETE CASCADE) CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE TABLE likes (id INT AUTO_INCREMENT PRIMARY KEY, id_user INT, id_bookmark INT, FOREIGN KEY (id_user) REFERENCES user(id) ON DELETE CASCADE, FOREIGN KEY (id_bookmark) REFERENCES bookmark(id) ON DELETE CASCADE, UNIQUE KEY (id_user, id_bookmark)) CHARACTER SET utf8 COLLATE utf8_general_ci;

INSERT INTO user(name, email, password, confirmed) VALUES ('disquete', 'disquete@disquete.com', '1234', 1);
INSERT INTO user(name, email, password, confirmed) VALUES ('pepe', 'pepe@pepe.com', '1234', 1);
INSERT INTO user(name, email, password, confirmed) VALUES ('paco', 'macaco@gmail.com', '1234', 1);
INSERT INTO tag(tag) values('google'), ('search'), ('test'), ('bookmark'), ('social'), ('delicious');
INSERT INTO bookmark(url, title, annotation, description, type, id_user) VALUES ('https://www.google.com', 'google', 'the most popular search engine', 'Search Engine', 1, 3);
INSERT INTO bookmark(url, title, annotation, description, likes, id_user) VALUES ('http://del.icio.us', 'Delicious', 'the page is on maintenance', 'Original page of Delicious!', 10000, 1);
INSERT INTO bookmark(url, title, annotation, description, likes, id_user) VALUES ('http://www.iesaguadulce.es/centro/', 'IES-Aguadulce', 'popular instituto', 'Instituto de Educación Secundaria Aguadulce Roquetas de Mar', 5000, 2);
INSERT INTO bookmark_tag VALUES(1, 1), (1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (2, 5), (3, 3);
SELECT b.title as title, b.url as url, b.annotation as annotation, b.description as description, GROUP_CONCAT(t.tag SEPARATOR ",") as tags, b.likes as likes, u.name AS user FROM bookmark b INNER JOIN user u ON u.id=b.id_user INNER JOIN bookmark_tag bt ON b.id=bt.id_bookmark INNER JOIN tag t ON bt.id_tag=t.id GROUP BY B.TITLE ORDER BY likes DESC LIMIT 10;
SELECT b.title, b.url, b.annotation, b.description, GROUP_CONCAT(t.tag SEPARATOR ', ') as tags, b.likes, u.name AS user FROM bookmark b INNER JOIN user u ON u.id=b.id_user LEFT JOIN bookmark_tag bt ON b.id=bt.id_bookmark LEFT JOIN tag t ON bt.id_tag=t.id GROUP BY b.title;
ORDER BY b.likes DESC 
LIMIT 10;
DELIMITER $$
DROP PROCEDURE IF EXISTS add_bookmark;
CREATE PROCEDURE add_bookmark(
    IN p_url VARCHAR(2047),
    IN p_title VARCHAR(100),
    IN p_annotation VARCHAR(500),
    IN p_description VARCHAR(2000),
    IN p_id_user INT,
    IN p_tags VARCHAR(1000),
    IN p_type INT
)
BEGIN
    DECLARE tag_list_length INT;
    DECLARE i INT;
    DECLARE tag_name VARCHAR(100);
    DECLARE tag_id INT;
    DECLARE done INT DEFAULT FALSE;

    -- Insert the bookmark with the type specified
    INSERT INTO bookmark(url, title, annotation, description, id_user, type)
    VALUES(p_url, p_title, p_annotation, p_description, p_id_user, p_type);

    -- Get the ID of the inserted bookmark
    SET @bookmark_id = LAST_INSERT_ID();

    -- Split the list of tags
    SET tag_list_length = LENGTH(p_tags) - LENGTH(REPLACE(p_tags, ',', '')) + 1;

    SET i = 1;
    WHILE i <= tag_list_length DO
        SET tag_name = SUBSTRING_INDEX(SUBSTRING_INDEX(p_tags, ',', i), ',', -1);
        SET tag_name = TRIM(tag_name);

        -- Check if the tag exists
        SELECT id INTO tag_id FROM tag WHERE tag = tag_name LIMIT 1;

        -- If the tag doesn't exist, insert it
        IF tag_id IS NULL THEN
            INSERT INTO tag(tag) VALUES(tag_name);
            SET tag_id = LAST_INSERT_ID();
        END IF;

        -- Add the relationship between the bookmark and the tag
        INSERT INTO bookmark_tag(id_bookmark, id_tag) VALUES(@bookmark_id, tag_id);

        SET i = i + 1;
    END WHILE;
END $$
DELIMITER ;
-- Modify the following lines in production
CREATE USER bellicious@'localhost' IDENTIFIED BY 'bellicious';
GRANT ALL ON bellicious.* TO bellicious@'localhost';
