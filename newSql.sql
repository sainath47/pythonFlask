create database dfx ;

use dfx ;

show tables ;

drop table countries ;

CREATE TABLE countries (
    id INT PRIMARY KEY AUTO_INCREMENT, -- Use appropriate data type and auto-increment syntax
    name VARCHAR(255) NOT NULL,
    country CHAR(20) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    unicode VARCHAR(200) NOT NULL,
    image VARCHAR(255) NOT NULL
);

select * from countries ;




select * from countries ;


select * from lease_data ORDER BY updated_at DESC ; 
SELECT * FROM lease_data WHERE is_deleted = FALSE ORDER BY updated_at DESC;
SELECT * FROM lease_data WHERE user_id= 'himanshijain201@gmail.com' ORDER BY updated_at DESC;

ALTER TABLE lease_data
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

ALTER TABLE lease_data
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

select * from lease_data;


CREATE TABLE user_details (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255),
    email VARCHAR(255),
    mobile VARCHAR(15),
    password VARCHAR(255),
    organisation VARCHAR(255)
);




select * from user_details ;