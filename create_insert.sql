CREATE TABLE insurance (
    insurance_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE hospital (
    hospital_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);

CREATE TABLE User (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    firstname VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    email_address VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type ENUM('insurance_provider', 'hospital') NOT NULL,
    insurance_id INT,
    hospital_id INT,
    FOREIGN KEY (insurance_id) REFERENCES insurance(insurance_id),
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id)
);

CREATE TABLE patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    contact_info VARCHAR(255)
);


CREATE TABLE medical_procedure (
    procedure_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    cost DECIMAL(10, 2) NOT NULL
);


CREATE TABLE claim (
    claim_id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT,
    insurance_id INT,
    patient_id INT,
    procedure_id INT,
    status ENUM('Approved', 'Pending', 'Rejected') NOT NULL,
    date DATE,
    total_amount DECIMAL(10, 2),
    covered_amount DECIMAL(10, 2),
    deductible_amount DECIMAL(10, 2) GENERATED ALWAYS AS (total_amount - covered_amount) STORED,
    description TEXT,
    FOREIGN KEY (hospital_id) REFERENCES hospital(hospital_id) ON DELETE CASCADE,
    FOREIGN KEY (insurance_id) REFERENCES insurance(insurance_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (procedure_id) REFERENCES medical_procedure(procedure_id) ON DELETE CASCADE
);

CREATE TABLE search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_first VARCHAR(50) NOT NULL,
    user_last VARCHAR(50) NOT NULL,
    search_term VARCHAR(255) NOT NULL,
    search_by ENUM('Hospital', 'Insurance', 'Patient', 'Procedure') NOT NULL,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comment (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    claim_id INT NOT NULL,
    comment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comment_content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
    FOREIGN KEY (claim_id) REFERENCES claim(claim_id) ON DELETE CASCADE
);

CREATE TABLE feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback_content TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE
);

CREATE TABLE edit_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_first VARCHAR(50) NOT NULL,
    user_last VARCHAR(50) NOT NULL,
    claim_id INT NOT NULL,
    edit_type ENUM('change_status', 'delete', 'create') NOT NULL,
    edit_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




INSERT INTO insurance (name, phone_number)
VALUES ('Kaiser', '3569871029'),
       ('Aetna', '5714265153'),
       ('UnitedHealthcare', '8005551212'),
       ('Blue Cross Blue Shield', '8881234567'),
       ('Humana', '8779876543'),
       ('Anthem', '8665554321'),
       ('Cigna', '5109938339');

INSERT INTO hospital (name, address, phone_number)
VALUES ('Palo Alto Medical Foundation','123 Main Street, Palo Alto, CA 62701', '1248874345'),
       ('Washington Hospital','456 Elm Avenue, Fairfax, VA 12345', '3569871029'),
       ('Mayo Clinic', '200 1st St SW, Rochester, MN 55905', '5072842511'),
       ('Cleveland Clinic', '9500 Euclid Ave, Cleveland, OH 44195', '2164442200'),
       ('Johns Hopkins Hospital', '1800 Orleans St, Baltimore, MD 21287', '4109555000'),
       ('Massachusetts General Hospital', '55 Fruit St, Boston, MA 02114', '6177262000'),
       ('Stanford Hospital','789 Oak Lane, Stanford, CA 98765', '6784559992');

INSERT INTO User (username, firstname, lastname, email_address, password_hash, user_type, insurance_id, hospital_id)
VALUES 
    ('ins_provider1', 'John', 'Doe', 'john@example.com', 'hashed_password', 'insurance_provider', 1, NULL),
    ('hospital_staff1', 'Jane', 'Smith', 'jane@example.com', 'hashed_password', 'hospital', NULL, 1),
    ('hospital_staff2', 'Michael', 'Johnson', 'michael@example.com', 'hashed_password', 'hospital', NULL, 2);

INSERT INTO patient (name, date_of_birth, contact_info)
VALUES ('John Doe', '1990-05-15', 'john.doe@example.com'),
       ('Jane Smith', '1985-08-20', 'jane.smith@example.com'),
       ('Michael Johnson', '1978-12-10', 'michael.johnson@example.com'),
       ('Alice Johnson', '1980-09-25', 'alice.johnson@example.com'),
       ('Bob Williams', '1975-06-12', 'bob.williams@example.com'),
       ('Carol Brown', '1995-03-08', 'carol.brown@example.com'),
       ('David Lee', '1967-11-18', 'david.lee@example.com'),
       ('Emma Davis', '2000-02-29', 'emma.davis@example.com');


INSERT INTO medical_procedure (name, description, cost) 
VALUES ('Knee Replacement Surgery', 'A surgical procedure to replace the knee joint with an artificial one.', 15000.00),
       ('Cataract Surgery', 'A surgical procedure to remove the lens of the eye and replace it with an artificial one.', 12000.00),
       ('Heart Bypass Surgery', 'A surgical procedure to reroute blood around a blocked artery in the heart.', 20000.00),
       ('Hip Replacement Surgery', 'A surgical procedure to replace the hip joint with an artificial one.', 18000.00),
       ('Appendectomy', 'A surgical procedure to remove the appendix.', 6000.00),
       ('Hernia Repair Surgery', 'A surgical procedure to repair a hernia.', 7000.00),
       ('Colonoscopy', 'A procedure to examine the colon for abnormalities.', 3000.00),
       ('Mammogram', 'A procedure to screen for breast cancer.', 1500.00),
       ('Endoscopy', 'A procedure to examine the digestive tract.', 4000.00),
       ('Laparoscopic Cholecystectomy', 'A surgical procedure to remove the gallbladder using a laparoscope.', 8000.00);


INSERT INTO claim (hospital_id, insurance_id, patient_id, procedure_id, status, date, total_amount, covered_amount, description)
VALUES (2, 2, 1, 1, 'Approved', '2024-03-15', 1500.00, 1200.00, 'successful, patient currently in recovery'),
	   (3, 2, 2, 2, 'Pending', '2024-03-20', 2500.00, 2000.00, 'procedure changes, price needs to be reflected'),
       (1, 1, 1, 1, 'Pending', '2024-04-10', 6000.00, 4800.00, 'Awaiting approval from insurance'),
       (2, 2, 2, 2, 'Approved', '2024-04-12', 7000.00, 5600.00, 'Claim successfully processed'),
       (3, 3, 3, 3, 'Rejected', '2024-04-15', 3000.00, 0.00, 'Procedure not covered by insurance'),
       (4, 4, 4, 4, 'Pending', '2024-04-18', 8000.00, 6400.00, 'Waiting for additional documentation'),
       (5, 5, 5, 5, 'Approved', '2024-04-20', 4500.00, 3600.00, 'Claim processed successfully'),
       (6, 6, 1, 1, 'Pending', '2024-04-22', 9000.00, 7200.00, 'Awaiting insurance review'),
       (7, 7, 2, 2, 'Rejected', '2024-04-25', 3500.00, 0.00, 'Insufficient coverage for procedure'),
       (1, 1, 3, 3, 'Approved', '2024-04-28', 2000.00, 1600.00, 'Claim processed successfully'),
       (2, 2, 4, 4, 'Pending', '2024-05-01', 6000.00, 4800.00, 'Under review by insurance'),
       (3, 3, 5, 5, 'Pending', '2024-05-04', 5500.00, 4400.00, 'Awaiting approval from insurance'),
       (4, 4, 1, 1, 'Approved', '2024-05-07', 2500.00, 2000.00, 'Claim processed successfully'),
       (5, 5, 2, 2, 'Rejected', '2024-05-10', 8000.00, 6400.00, 'Insufficient coverage for procedure'),
       (6, 6, 3, 3, 'Pending', '2024-05-13', 4000.00, 3200.00, 'Awaiting approval from insurance'),
       (7, 7, 4, 4, 'Approved', '2024-05-16', 3500.00, 2800.00, 'Claim processed successfully'),
       (1, 1, 5, 5, 'Pending', '2024-05-19', 5000.00, 4000.00, 'Under review by insurance'),
       (2, 2, 1, 1, 'Approved', '2024-05-22', 6000.00, 4800.00, 'Claim processed successfully'),
       (3, 3, 2, 2, 'Rejected', '2024-05-25', 3000.00, 0.00, 'Insufficient coverage for procedure'),
       (4, 4, 3, 3, 'Pending', '2024-05-28', 7000.00, 5600.00, 'Awaiting approval from insurance'),
       (5, 5, 4, 4, 'Approved', '2024-06-01', 2500.00, 2000.00, 'Claim processed successfully'),
       (6, 6, 5, 5, 'Pending', '2024-06-04', 6000.00, 4800.00, 'Under review by insurance'),
	   (1, 2, 3, 3, 'Rejected', '2024-03-25', 1800.00, 0.00, 'incorrect claim, forwarding to Cigna');


INSERT INTO search_history (user_id, user_first, user_last, search_term, search_by)
VALUES (1, 'Bob', 'Ross', 'Knee Replacement Surgery', 'Procedure'),
       (2, 'Michael', 'Phelps', 'Cataract Surgery', 'Procedure'),
       (3, 'Erl', 'Bodgins', 'Heart Bypass Surgery', 'Procedure');

INSERT INTO comment (user_id, claim_id, comment_content)
VALUES (1, 1, 'I have all the necessary documents for this claim.'),
       (2, 2, 'I need more information about the procedure costs.'),
       (1, 3, 'The claim seems to be in order, but I have some concerns about the coverage.');

INSERT INTO feedback (user_id, feedback_content)
VALUES (1, 'The user interface is very intuitive and easy to navigate.'),
       (2, 'I would like to see more options for customizing my dashboard.');

INSERT INTO edit_log (user_id, user_first, user_last, claim_id, edit_type)
VALUES (1,'Tommy', 'Gandalf', 1, 'change_status'),
       (2,'Mary', 'Poppins', 2, 'delete'),
       (1,'Andrew', 'Aurora',3, 'create');