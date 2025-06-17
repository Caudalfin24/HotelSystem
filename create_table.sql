-- 用户表
CREATE TABLE User (
    userId INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'hotel', 'admin') NOT NULL
);

-- 权限表
CREATE TABLE Permission (
    permissionId INT PRIMARY KEY AUTO_INCREMENT,
    endpoint VARCHAR(100) NOT NULL
);

INSERT INTO Permission (endpoint)
VALUES ('user.change_password'), ('customer.booking_hotels'), ('customer.view_bookings'), ('hotel.manage_hotel')

-- 用户-权限表
CREATE TABLE UserPermission (
    userId INT,
    permissionId INT,
    PRIMARY KEY(userId, permissionId),
    FOREIGN KEY (userId) REFERENCES User(userId) ON DELETE CASCADE,
    FOREIGN KEY (permissionId) REFERENCES Permission(permissionId) ON DELETE CASCADE
);

-- 客户表
CREATE TABLE Customer (
    customerId INT PRIMARY KEY,
    customerName VARCHAR(10),
    email VARCHAR(100),
    customerPhone VARCHAR(20),
    age INT,
    sex CHAR(1),
    FOREIGN KEY (customerId) REFERENCES User(userId) ON DELETE CASCADE
);


-- 客户添加触发器
DELIMITER //
CREATE TRIGGER after_user_insert
AFTER INSERT ON User
FOR EACH ROW
BEGIN
    IF NEW.role = 'customer' THEN
        INSERT INTO Customer (customerId)
        VALUES (NEW.userId);

        INSERT INTO UserPermission (userId, permissionId)
        VALUES (NEW.userId, 1), (NEW.userId, 2), (NEW.userId, 3);
    END IF;
    IF NEW.role = 'hotel' THEN
        INSERT INTO UserPermission (userId, permissionId)
        VALUES (NEW.userId, 1), (NEW.userId, 4);
    END IF;
END;
//
DELIMITER ;


-- 创建酒店表
CREATE TABLE Hotel (
    hotelId int PRIMARY KEY AUTO_INCREMENT,
    hotelName VARCHAR(100),
    ownerId int NOT NULL,
    city VARCHAR(20),
    address VARCHAR(100),
    hotelPhone VARCHAR(20),
    rating int,
    FOREIGN KEY (ownerId) REFERENCES User(userId) ON DELETE CASCADE
);

-- 创建房间表
CREATE TABLE Room (
    roomId INT PRIMARY KEY AUTO_INCREMENT,
    hotelId INT NOT NULL,
    roomType VARCHAR(50),
    price DECIMAL(10, 2),
    totalNum INT,
    available INT,
    description TEXT,
    CONSTRAINT fk_hotel FOREIGN KEY (hotelId) REFERENCES Hotel(hotelId) ON DELETE CASCADE,
    CONSTRAINT chk_available CHECK (available <= totalNum AND available >= 0)
);


CREATE TABLE Booking(
    bookingId INT PRIMARY KEY AUTO_INCREMENT,
    customerId INT NOT NULL, 
    roomId INT NOT NULL, 
    checkIn DATE NOT NULL, 
    checkOut DATE NOT NULL, 
    totalPrice DECIMAL(10,2) NOT NULL,
    status ENUM('notCheckIn', 'checkIn', 'checkOut') NOT NULL,
    CONSTRAINT fk_customer FOREIGN KEY (customerId) REFERENCES Customer(customerId) ON DELETE CASCADE,
    CONSTRAINT fk_room FOREIGN KEY (roomId) REFERENCES Room(roomId) ON DELETE CASCADE
);