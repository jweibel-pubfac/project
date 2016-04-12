SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS auth;
DROP TABLE IF EXISTS label;
DROP TABLE IF EXISTS article;

CREATE TABLE article (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    title VARCHAR(50) NOT NULL, 
    content_md MEDIUMTEXT NOT NULL, 
    content_html MEDIUMTEXT NOT NULL, 
    time DATETIME NOT NULL,
    sort text not null,
    visit int(9) Default 0,
    image text
    
);

CREATE TABLE label (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    detail VARCHAR(30) NOT NULL, 
    FOREIGN KEY(article_id) REFERENCES article(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE auth (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(20) NOT NULL, 
    password VARCHAR(40) NOT NULL 
);
