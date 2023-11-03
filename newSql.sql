create database dfx ;

use dfx ;

show tables ;





CREATE TABLE user_details (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255),
    email VARCHAR(255),
    mobile VARCHAR(15),
    password VARCHAR(255),
    organisation VARCHAR(255)
);

drop table user_details;

select * from user_details ;