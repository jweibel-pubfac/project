SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS student;

CREATE TABLE student (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    name VARCHAR(50) NOT NULL, 
    major text NOT NULL,
    sort text not null,
    teacher text not null,
    class_hour text not null,
    telephone text not null,
    qq text not null,
    time DATETIME NOT NULL
);

CREATE TABLE admin (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
    username VARCHAR(20) NOT NULL, 
    password VARCHAR(40) NOT NULL 
);
