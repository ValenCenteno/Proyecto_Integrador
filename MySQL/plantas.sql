CREATE TABLE plantas (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    humedad VARCHAR(20),
    porcentaje DECIMAL(5,2) CHECK (porcentaje >= 0 AND porcentaje <= 100),
    PRIMARY KEY (id)
);
