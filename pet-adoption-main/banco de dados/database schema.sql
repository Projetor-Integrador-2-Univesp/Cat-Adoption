create schema bastet;
use bastet;
CREATE TABLE adotante (
    nome      VARCHAR(100) NOT NULL,
    cpf       CHAR(11)     PRIMARY KEY,
    email     VARCHAR(150) NOT NULL UNIQUE,
    endereco  VARCHAR(255),
    telefone  VARCHAR(15)
);

CREATE TABLE usuario_sistema (
    id_usuario INT          AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL UNIQUE,
    telefone   VARCHAR(15),
    senha      VARCHAR(255) NOT NULL
);

CREATE TABLE pet (
    id_pet       INT         AUTO_INCREMENT PRIMARY KEY,
    data_entrada DATE        NOT NULL DEFAULT (CURRENT_DATE),
    idade        INT,
    sexo         CHAR(1)     CHECK (sexo IN ('M', 'F')),
    cor          VARCHAR(50),
    descricao    VARCHAR(500),
    status       VARCHAR(20) NOT NULL DEFAULT 'disponivel'
                             CHECK (status IN ('disponivel', 'adotado', 'em_tratamento')),
    fk_usuario_sistema_id_usuario INT NOT NULL
);

CREATE TABLE adocao (
    id_adocao         INT      AUTO_INCREMENT PRIMARY KEY,
    data_adocao       DATE     NOT NULL DEFAULT (CURRENT_DATE),
    obs               VARCHAR(500),
    termo_compromisso BOOLEAN  NOT NULL DEFAULT FALSE,
    fk_pet_id_pet     INT      NOT NULL,
    fk_adotante_cpf   CHAR(11) NOT NULL,
    fk_usuario_sistema_id_usuario INT NOT NULL
);

ALTER TABLE pet ADD CONSTRAINT FK_pet_2
    FOREIGN KEY (fk_usuario_sistema_id_usuario)
    REFERENCES usuario_sistema (id_usuario)
    ON DELETE RESTRICT;

ALTER TABLE adocao ADD CONSTRAINT FK_adocao_2
    FOREIGN KEY (fk_pet_id_pet)
    REFERENCES pet (id_pet)
    ON DELETE CASCADE;

ALTER TABLE adocao ADD CONSTRAINT FK_adocao_3
    FOREIGN KEY (fk_adotante_cpf)
    REFERENCES adotante (cpf)
    ON DELETE RESTRICT;

ALTER TABLE adocao ADD CONSTRAINT FK_adocao_4
    FOREIGN KEY (fk_usuario_sistema_id_usuario)
    REFERENCES usuario_sistema (id_usuario)
    ON DELETE RESTRICT;