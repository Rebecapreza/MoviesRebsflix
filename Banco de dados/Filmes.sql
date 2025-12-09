-- Criação da base de dados
DROP DATABASE IF EXISTS Filmes;
CREATE DATABASE Filmes;
USE Filmes;

-- Tabelas principais
-- Diretor
CREATE TABLE diretor (
    id_diretor INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    sobrenome VARCHAR(100),
    genero VARCHAR(100),
    nacionalidade VARCHAR(100)
);

-- Generos
CREATE TABLE generos (
    id_generos INT AUTO_INCREMENT PRIMARY KEY,
    generos VARCHAR(100)
);

-- Pais
CREATE TABLE pais (
    id_pais INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100)
);

-- Usuários
CREATE TABLE usuarios (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR (100) NOT NULL UNIQUE,
    email VARCHAR (255) NOT NULL UNIQUE,
    senha VARCHAR (255) NOT NULL
);

-- Administrador
CREATE TABLE administradores (
    id_adm INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR (255) NOT NULL UNIQUE,
    senha VARCHAR (255) NOT NULL
);

-- Filme
CREATE TABLE filme (
    id_filme INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    sinopse TEXT,
    poster_url VARCHAR(255),
    ano YEAR,
    tp_duracao TIME,
    orcamento DECIMAL(15,2),
    id_user INT,
    status ENUM('pendente', 'aprovado', 'rejeitado') NOT NULL DEFAULT 'pendente',
    FOREIGN KEY (id_user) REFERENCES usuarios(id_user)
);

-- Produtora
CREATE TABLE produtora (
    id_produtora INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255)
);

-- Atores
CREATE TABLE atores (
    id_atores INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255),
    sobrenome VARCHAR(255),
    genero VARCHAR(255),
    nacionalidade VARCHAR(255)
);

-- Linguagem
CREATE TABLE linguagem (
    id_linguagem INT AUTO_INCREMENT PRIMARY KEY,
    lingua VARCHAR(255)
);

-- Tabelas de relacionamento
-- Diretor e filme
CREATE TABLE filme_diretor (
    id_filme_diretor INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_diretor INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_diretor) REFERENCES diretor(id_diretor)
);

-- Generos e filme
CREATE TABLE generos_filme (
    id_generos_filme INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_generos INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_generos) REFERENCES generos(id_generos)
);

-- Pais e filme
CREATE TABLE pais_filme (
    id_pais_filme INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_pais INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_pais) REFERENCES pais(id_pais)
);

-- Produtora e filme
CREATE TABLE produtora_filme (
    id_produtora_filme INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_produtora INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_produtora) REFERENCES produtora(id_produtora)
);

-- Ator e filme
CREATE TABLE atores_filme (
    id_atores_filme INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_atores INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_atores) REFERENCES atores(id_atores)
);

-- Linguagem e filme
CREATE TABLE linguagem_filme (
    id_linguagem_filme INT AUTO_INCREMENT PRIMARY KEY,
    id_filme INT,
    id_linguagem INT,
    FOREIGN KEY (id_filme) REFERENCES filme(id_filme),
    FOREIGN KEY (id_linguagem) REFERENCES linguagem(id_linguagem)
);

-- Inserindo dados

-- Gêneros
INSERT INTO generos (generos) VALUES
('Fantasia'), 
('Terror'),   
('Ação'),     
('Romance'),  
('Comédia'),  
('Drama');    

-- Usuários 
INSERT INTO usuarios (nome, email, senha) VALUES
('Rebeca', 'Rebs@gmail.com', '1234');

-- Administrador 
INSERT INTO administradores (email, senha) VALUES
('administrador@ADM.com', '1234'); 

-- Paises
INSERT INTO pais (nome) VALUES
('EUA'),          
('Brasil'),       
('Portugal'),     
('Reino Unido'),  
('Alemanha'),     
('Espanhol');     

-- Linguagem
INSERT INTO linguagem (lingua) VALUES
('Português'), 
('Inglês'),    
('Espanhol');  

-- Produtoras
INSERT INTO produtora (nome) VALUES
('Walt Disney Animation Studios'), 
('Marvel'),                        
('Paramount Pictures'),            
('Universal Pictures'),            
('Warner Bros. Pictures'),         
('CBS Films'),                     
('New Line Cinema'),               
('Constantin Film'),               
('Voltage Pictures'),              
('Netflix'),                       
('Happy Madison Productions'),     
('Mattel Entertainment');          

-- Diretores (INSERIDO)
INSERT INTO diretor (nome, sobrenome, genero, nacionalidade) VALUES
('Brian', 'De Palma', 'Masculino', 'Americano'),   -- Missão: Impossível
('Anthony', 'Russo', 'Masculino', 'Americano'),     -- Vingadores: Ultimato
('Joe', 'Russo', 'Masculino', 'Americano'),         -- Vingadores: Ultimato
('Christopher', 'Nolan', 'Masculino', 'Britânico'), -- Batman: O Cavaleiro das Trevas
('Rob', 'Cohen', 'Masculino', 'Americano'),         -- Velozes e Furiosos
('Christian', 'Ditter', 'Masculino', 'Alemão'),     -- Simplesmente Acontece
('Susan', 'Johnson', 'Feminino', 'Americana'),      -- Para Todos os Garotos
('Nick', 'Cassavetes', 'Masculino', 'Americano'),   -- Diário de Uma Paixão
('Elizabeth', 'Allen', 'Feminino', 'Americana'),    -- Continências do Amor
('John', 'R. Leonetti', 'Masculino', 'Americano'),  -- Annabelle
('James', 'Wan', 'Masculino', 'Australiano'),       -- Invocação do Mal
('John', 'Leonetti', 'Masculino', 'Americano'),     -- O Silêncio
('Ben', 'Howling', 'Masculino', 'Australiano'),     -- Cargo
('Yolanda', 'Ramke', 'Feminino', 'Australiana'),    -- Cargo
('Dennis', 'Dugan', 'Masculino', 'Americano'),      -- Esposa de Mentirinha / Gente Grande
('Peter', 'Segal', 'Masculino', 'Americano'),       -- Como se Fosse a Primeira Vez
('Sammi', 'Cohen', 'Feminino', 'Americana'),        -- Você Não Tá Convidada
('Nathan', 'Greno', 'Masculino', 'Americano'),      -- Enrolados
('Byron', 'Howard', 'Masculino', 'Americano'),      -- Enrolados
('David', 'Hand', 'Masculino', 'Americano'),        -- Bambi
('William', 'Roberts', 'Masculino', 'Americano'),   -- Bambi
('Mel', 'Dank', 'Masculino', 'Americano'),          -- Bambi
('Ezekiel', 'Norton', 'Masculino', 'Americano'),    -- Barbie: Escola de Princesas
('Steven', 'Spielberg', 'Masculino', 'Americano'),  -- O Bom Gigante Amigo
('Pilar', 'Palomero', 'Feminino', 'Espanhola'),     -- A Lista da Minha Vida
('Justin', 'Baldoni', 'Masculino', 'Americano'),    -- A Cinco Passos de Você
('Thea', 'Sharrock', 'Feminino', 'Britânica'),      -- Como Eu Era Antes de Você
('Scott', 'Speer', 'Masculino', 'Americano');       -- O Sol da Meia Noite


-- Filmes
-- Filmes de Ação
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('Missão: Impossível', 'Agente Ethan Hunt é incriminado e precisa provar sua inocência descobrindo um agente duplo na sua própria equipe.', 'https://i.pinimg.com/1200x/14/4b/46/144b46288f99e9711c2dd8c95894ad9a.jpg', '1996', '01:50:00', 80000000.00, 1),
('Vingadores: Ultimato', 'Os heróis sobreviventes buscam uma maneira de reverter o estalar de dedos de Thanos e trazer de volta seus entes queridos.', 'https://i.pinimg.com/736x/cd/b3/b6/cdb3b63eb3ac1cf8faab32770c6dc3b5.jpg', '2019', '03:01:00', 356000000.00, 1),
('Batman: O Cavaleiro das Trevas', 'O Batman se une ao Tenente Gordon e ao promotor Harvey Dent para combater o Coringa, um novo gênio do crime em Gotham.', 'https://i.pinimg.com/736x/7e/84/a3/7e84a359c9ea71dbdeb24d4541b9f16d.jpg', '2008', '02:32:00', 185000000.00, 1),
('Velozes e Furiosos', 'Um policial disfarçado se infiltra no submundo das corridas de rua para investigar uma série de roubos de caminhões.', 'https://i.pinimg.com/1200x/3e/c6/f9/3ec6f9aa0f0780fb467b5d551d37c95d.jpg', '2001', '01:46:00', 38000000.00, 1); 

-- Filmes de Romance
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('Simplesmente Acontece', 'Melhores amigos desde a infância, Rosie e Alex se separam e tentam se reconectar ao longo dos anos, apesar dos obstáculos.', 'https://i.pinimg.com/736x/b7/71/2b/b7712b05ce4965623926a4a1543ed2ff.jpg', '2014', '01:42:00', NULL, 1), 
('Para Todos os Garotos que Já Amei', 'A vida amorosa de uma adolescente vira de cabeça para baixo quando suas cartas de amor secretas são enviadas misteriosamente a todos os seus ex-crushes.', 'https://i.pinimg.com/1200x/74/37/d0/7437d0f79c0fda8f449aa9df8fea0c3c.jpg', '2018', '01:39:00', 20000000.00, 1), 
('Diário de Uma Paixão', 'Uma história épica de um amor que supera barreiras sociais na juventude e a passagem do tempo na velhice.', 'https://i.pinimg.com/1200x/91/8b/88/918b88576de32abf6e791aee60be5fb5.jpg', '2004', '02:03:00', 29000000.00, 1), 
('Continências do Amor', 'Uma cantora e um fuzileiro naval se casam por conveniência, mas acabam se apaixonando de verdade.', 'https://i.pinimg.com/1200x/59/89/ab/5989abffd787b92245d70b79e6729073.jpg', '2022', '02:02:00', NULL, 1);

-- Filmes de Terror
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('Annabelle', 'Um casal é aterrorizado por uma boneca vintage possuída por uma entidade maligna.', 'https://i.pinimg.com/1200x/6a/39/5f/6a395f05abaa078aebb6cf68f030727c.jpg', '2014', '01:39:00', 6500000.00, 1),
('Invocação do Mal', 'Investigadores paranormais ajudam uma família que está sendo aterrorizada por uma presença sombria em sua fazenda.', 'https://i.pinimg.com/1200x/88/16/b0/8816b05be4567829bce29fd49fb1b7ea.jpg', '2013', '01:52:00', 20000000.00, 1),
('O Silêncio', 'Uma família precisa se esconder e viver em silêncio após o surgimento de criaturas mortais guiadas pelo som.', 'https://i.pinimg.com/736x/1b/ce/73/1bce73e365725afaf7024905475a9da6.jpg', '2019', '01:30:00', NULL, 1), 
('Cargo', 'Um pai infectado em uma Austrália pós-apocalíptica tem 48 horas para encontrar alguém que proteja sua bebê antes de se transformar.', 'https://i.pinimg.com/736x/c0/3e/77/c03e77d8a0894b80fdd6567655c3b135.jpg', '2018', '01:45:00', NULL, 1); 

-- Filmes de Comédia
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('Esposa de Mentirinha', 'Um cirurgião plástico solteiro convence sua assistente a fingir ser sua esposa para encobrir uma mentira.', 'https://i.pinimg.com/73x/4b/4e/39/4b4e39db5c7d8c4864d1de5cf37a86da.jpg', '2011', '01:57:00', 80000000.00, 1),
('Como se Fosse a Primeira Vez', 'Um veterinário se apaixona por uma mulher com perda de memória de curto prazo e precisa conquistá-la todos os dias.', 'https://i.pinimg.com/73x/c4/62/75/c46275ac50d84b8c225e6d6b25c467b4.jpg', '2004', '01:39:00', 75000000.00, 1), 
('Gente Grande', 'Cinco amigos de infância se reúnem para um feriado de fim de semana na casa do lago após o falecimento de seu treinador de basquete.', 'https://i.pinimg.com/73x/5f/05/0c/5f050c25bb18771b4a30045526e75b08.jpg', '2010', '01:42:00', 80000000.00, 1), 
('Você Não Tá Convidada Pra o Meu Bat Mitzvá!', 'Duas melhores amigas planejam seus luxuosos Bat Mitzvahs, mas uma rixa causada por um garoto ameaça arruinar tudo.', 'https://i.pinimg.com/73x/89/98/60/8998609c10f2bbc4738f1ecdaf75f3ff.jpg', '2023', '01:43:00', NULL, 1);   

-- Filmes de Fantasia
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('Enrolados', 'Uma princesa de longos cabelos dourados é mantida em uma torre por uma velha bruxa, mas sonha em ver as lanternas flutuantes.', 'https://i.pinimg.com/73x/eb/e2/9f/ebe29f22a9007e711f61b507287e0033.jpg', '2010', '01:40:00', 260000000.00, 1), 
('Bambi', 'Um jovem cervo aprende sobre a vida na floresta com seus amigos Thumper e Flower.', 'https://i.pinimg.com/1200x/59/1b/14/591b14548e85e54bfeec704356c66131.jpg', '1942', '01:10:00', 858000.00, 1), 
('Barbie: Escola de Princesas', 'Barbie descobre que é uma princesa com destino a uma escola mágica onde aprende etiqueta real.', 'https://i.pinimg.com/1200x/80/48/1b/80481b3b0b51f3ee0899142bda008b90.jpg', '2011', '01:23:00', NULL, 1), 
('O Bom Gigante Amigo', 'Uma menina de 10 anos se torna amiga de um gigante bondoso, que a leva para o País dos Sonhos.', 'https://i.pinimg.com/73x/95/4a/a5/954aa50ea8449583ca7998a696abb026.jpg', '2016', '01:57:00', 140000000.00, 1);

-- Filmes de Drama
INSERT INTO filme (titulo, sinopse, poster_url, ano, tp_duracao, orcamento, id_user) VALUES
('A Lista da Minha Vida', 'Uma jovem descobre uma antiga lista de desejos de sua adolescência e decide completá-la após um luto.', 'https://i.pinimg.com/1200x/a4/6c/28/a46c28b6e4abcc120b758f2a6ce27fb5.jpg', '2020', '01:47:00', NULL, 1), 
('A Cinco Passos de Você', 'Dois jovens com fibrose cística se apaixonam, mas precisam manter uma distância segura um do outro.', 'https://i.pinimg.com/73x/e0/69/ba/e069ba4b74a045184cc6676a503157dc.jpg', '2019', '01:56:00', NULL, 1), 
('Como Eu Era Antes de Você', 'Uma jovem de cidade pequena se torna cuidadora de um homem rico e tetraplégico, e os dois desenvolvem um laço profundo.', 'https://i.pinimg.com/1200x/b0/1f/5b/b01f5b5363bbc4ebdd66ce0e3c8b506e.jpg', '2016', '01:50:00', 20000000.00, 1), 
('O Sol da Meia Noite', 'Uma adolescente com uma rara doença que a impede de ter contato com a luz solar realiza o sonho de viver um romance.', 'https://i.pinimg.com/73x/dd/d9/c2/ddd9c250c94f650fe1c38b37c34bd133.jpg', '2018', '01:31:00', NULL, 1); 

-- Atores
-- Ação (Missão: Impossível, Vingadores: Ultimato, Batman, Velozes e Furiosos)
INSERT INTO atores (nome, sobrenome, genero, nacionalidade) VALUES
('Tom', 'Cruise', 'Masculino', 'Americano'),        -- Missão: Impossível
('Robert', 'Downey Jr.', 'Masculino', 'Americano'),  -- Vingadores: Ultimato
('Christian', 'Bale', 'Masculino', 'Britânico'),     -- Batman: O Cavaleiro das Trevas
('Vin', 'Diesel', 'Masculino', 'Americano'),         -- Velozes e Furiosos
('Heath', 'Ledger', 'Masculino', 'Australiano'),     -- Batman: O Cavaleiro das Trevas
('Chris', 'Evans', 'Masculino', 'Americano'),        -- Vingadores: Ultimato

-- Romance (Simplesmente Acontece, Para Todos os Garotos, Diário de Uma Paixão, Continências)
('Lily', 'Collins', 'Feminino', 'Britânica'),        -- Simplesmente Acontece
('Noah', 'Centineo', 'Masculino', 'Americano'),      -- Para Todos os Garotos
('Rachel', 'McAdams', 'Feminino', 'Canadense'),      -- Diário de Uma Paixão
('Ryan', 'Gosling', 'Masculino', 'Canadense'),       -- Diário de Uma Paixão
('Sofia', 'Carson', 'Feminino', 'Americana'),        -- Continências do Amor

-- Terror (Annabelle, Invocação do Mal, O Silêncio, Cargo)
('Vera', 'Farmiga', 'Feminino', 'Americana'),        -- ID 12 (Invocação do Mal
('Patrick', 'Wilson', 'Masculino', 'Americano'),     -- ID 13 (Invocação do Mal
('Kiernan', 'Shipka', 'Feminino', 'Americana'),      -- ID 14 (O Silêncio
('Martin', 'Freeman', 'Masculino', 'Britânico'),     -- ID 15 (Cargo

-- Comédia (Esposa de Mentirinha, Gente Grande, Bat Mitzvá)
('Adam', 'Sandler', 'Masculino', 'Americano'),       -- Esposa de Mentirinha, Gente Grande, Bat Mitzvá
('Drew', 'Barrymore', 'Feminino', 'Americana'),      -- Como se Fosse a Primeira Vez
('Jennifer', 'Aniston', 'Feminino', 'Americana'),    -- Esposa de Mentirinha
('Jackie', 'Sandler', 'Feminino', 'Americana'),      -- Você Não Tá Convidada

-- Fantasia (Enrolados, Bambi, O Bom Gigante Amigo)
('Zachary', 'Levi', 'Masculino', 'Americano'),       -- Voz de Flynn Rider - Enrolados
('Mandy', 'Moore', 'Feminino', 'Americana'),         -- Voz de Rapunzel - Enrolados
('Mark', 'Rylance', 'Masculino', 'Britânico'),       -- Voz do BGA - O Bom Gigante Amigo
('Dakota', 'Johnson', 'Feminino', 'Britânica'),      -- A Lista da Minha Vida
('Cole', 'Sprouse', 'Masculino', 'Americano'),       -- A Cinco Passos de Você
('Emilia', 'Clarke', 'Feminino', 'Britânica'),       -- Como Eu Era Antes de Você
('Bella', 'Thorne', 'Feminino', 'Americana');        -- O Sol da Meia Noite


-- Inserções nas Tabelas de Relacionamento (Muitos para Muitos)

-- Filme e Diretor
INSERT INTO filme_diretor (id_filme, id_diretor) VALUES
(1, 1),  -- Missão: Impossível - Brian De Palma
(2, 2),  -- Vingadores: Ultimato - Anthony Russo
(2, 3),  -- Vingadores: Ultimato - Joe Russo
(3, 4),  -- Batman: O Cavaleiro das Trevas - Christopher Nolan
(4, 5),  -- Velozes e Furiosos - Rob Cohen
(5, 6),  -- Simplesmente Acontece - Christian Ditter
(6, 7),  -- Para Todos os Garotos - Susan Johnson
(7, 8),  -- Diário de Uma Paixão - Nick Cassavetes
(8, 9),  -- Continências do Amor - Elizabeth Allen
(9, 10), -- Annabelle - John R. Leonetti
(10, 11),-- Invocação do Mal - James Wan
(11, 12),-- O Silêncio - John Leonetti
(12, 13),-- Cargo - Ben Howling
(12, 14),-- Cargo - Yolanda Ramke
(13, 15),-- Esposa de Mentirinha - Dennis Dugan
(14, 16),-- Como se Fosse a Primeira Vez - Peter Segal
(15, 15),-- Gente Grande - Dennis Dugan
(16, 17),-- Você Não Tá Convidada - Sammi Cohen
(17, 18),-- Enrolados - Nathan Greno
(17, 19),-- Enrolados - Byron Howard
(18, 20),-- Bambi - David Hand
(18, 21),-- Bambi - William Roberts
(18, 22),-- Bambi - Mel Dank
(19, 23),-- Barbie: Escola de Princesas - Ezekiel Norton
(20, 24),-- O Bom Gigante Amigo - Steven Spielberg
(21, 25),-- A Lista da Minha Vida - Pilar Palomero
(22, 26),-- A Cinco Passos de Você - Justin Baldoni
(23, 27),-- Como Eu Era Antes de Você - Thea Sharrock
(24, 28);-- O Sol da Meia Noite - Scott Speer

-- Filme e Gêneros
INSERT INTO generos_filme (id_filme, id_generos) VALUES
(1, 3), (1, 6), -- Missão: Impossível (Ação, Drama)
(2, 3), (2, 1), -- Vingadores: Ultimato (Ação, Fantasia)
(3, 3), (3, 6), -- Batman: O Cavaleiro das Trevas (Ação, Drama)
(4, 3),         -- Velozes e Furiosos (Ação)
(5, 4), (5, 6), -- Simplesmente Acontece (Romance, Drama)
(6, 4), (6, 5), -- Para Todos os Garotos (Romance, Comédia)
(7, 4), (7, 6), -- Diário de Uma Paixão (Romance, Drama)
(8, 4), (8, 6), -- Continências do Amor (Romance, Drama)
(9, 2),         -- Annabelle (Terror)
(10, 2),        -- Invocação do Mal (Terror)
(11, 2), (11, 3), -- O Silêncio (Terror, Ação)
(12, 2), (12, 6), -- Cargo (Terror, Drama)
(13, 5), (13, 4), -- Esposa de Mentirinha (Comédia, Romance)
(14, 5), (14, 4), -- Como se Fosse a Primeira Vez (Comédia, Romance)
(15, 5),          -- Gente Grande (Comédia)
(16, 5),          -- Você Não Tá Convidada (Comédia)
(17, 1), (17, 5), -- Enrolados (Fantasia, Comédia)
(18, 1), (18, 6), -- Bambi (Fantasia, Drama)
(19, 1),          -- Barbie: Escola de Princesas (Fantasia)
(20, 1), (20, 6), -- O Bom Gigante Amigo (Fantasia, Drama)
(21, 6),          -- A Lista da Minha Vida (Drama)
(22, 6), (22, 4), -- A Cinco Passos de Você (Drama, Romance)
(23, 6), (23, 4), -- Como Eu Era Antes de Você (Drama, Romance)
(24, 6), (24, 4); -- O Sol da Meia Noite (Drama, Romance)

-- Filme e Países
INSERT INTO pais_filme (id_filme, id_pais) VALUES
(1, 1), (1, 6), -- Missão: Impossível (EUA, Espanha) - apenas exemplo
(2, 1),         -- Vingadores: Ultimato (EUA)
(3, 1), (3, 4), -- Batman: O Cavaleiro das Trevas (EUA, Reino Unido)
(4, 1),         -- Velozes e Furiosos (EUA)
(5, 4),         -- Simplesmente Acontece (Reino Unido)
(6, 1),         -- Para Todos os Garotos (EUA)
(7, 1),         -- Diário de Uma Paixão (EUA)
(8, 1),         -- Continências do Amor (EUA)
(9, 1),         -- Annabelle (EUA)
(10, 1),        -- Invocação do Mal (EUA)
(11, 1),        -- O Silêncio (EUA)
(12, 2),        -- Cargo (Brasil) - Assumindo que o banco de dados tem dados globais
(13, 1),        -- Esposa de Mentirinha (EUA)
(14, 1),        -- Como se Fosse a Primeira Vez (EUA)
(15, 1),        -- Gente Grande (EUA)
(16, 1),        -- Você Não Tá Convidada (EUA)
(17, 1),        -- Enrolados (EUA)
(18, 1),        -- Bambi (EUA)
(19, 1),        -- Barbie: Escola de Princesas (EUA)
(20, 1),        -- O Bom Gigante Amigo (EUA)
(21, 6),        -- A Lista da Minha Vida (Espanhol)
(22, 1),        -- A Cinco Passos de Você (EUA)
(23, 4),        -- Como Eu Era Antes de Você (Reino Unido)
(24, 1);        -- O Sol da Meia Noite (EUA)

-- Filme e Produtoras
INSERT INTO produtora_filme (id_filme, id_produtora) VALUES
(1, 3),  -- Missão: Impossível (Paramount Pictures)
(2, 2),  -- Vingadores: Ultimato (Marvel)
(3, 5),  -- Batman: O Cavaleiro das Trevas (Warner Bros.)
(4, 4),  -- Velozes e Furiosos (Universal Pictures)
(5, 6),  -- Simplesmente Acontece (CBS Films)
(6, 10), -- Para Todos os Garotos (Netflix)
(7, 7),  -- Diário de Uma Paixão (New Line Cinema)
(8, 10), -- Continências do Amor (Netflix)
(9, 5),  -- Annabelle (Warner Bros.)
(10, 5), -- Invocação do Mal (Warner Bros.)
(11, 10),-- O Silêncio (Netflix)
(12, 10),-- Cargo (Netflix)
(13, 4), -- Esposa de Mentirinha (Universal Pictures)
(14, 4), -- Como se Fosse a Primeira Vez (Universal Pictures)
(15, 11),-- Gente Grande (Happy Madison)
(16, 10),-- Você Não Tá Convidada (Netflix)
(17, 1), -- Enrolados (Walt Disney)
(18, 1), -- Bambi (Walt Disney)
(19, 12),-- Barbie: Escola de Princesas (Mattel)
(20, 5), -- O Bom Gigante Amigo (Warner Bros.)
(21, 8), -- A Lista da Minha Vida (Constantin Film)
(22, 9), -- A Cinco Passos de Você (Voltage Pictures)
(23, 5), -- Como Eu Era Antes de Você (Warner Bros.)
(24, 5); -- O Sol da Meia Noite (Warner Bros.)

-- Filme e Atores
INSERT INTO atores_filme (id_filme, id_atores) VALUES
(1, 1),  -- Missão: Impossível - Tom Cruise
(2, 2),  -- Vingadores: Ultimato - Robert Downey Jr.
(2, 6),  -- Vingadores: Ultimato - Chris Evans
(3, 3),  -- Batman - Christian Bale
(3, 5),  -- Batman - Heath Ledger
(4, 4),  -- Velozes e Furiosos - Vin Diesel
(5, 7),  -- Simplesmente Acontece - Lily Collins
(6, 8),  -- Para Todos os Garotos - Noah Centineo
(7, 9),  -- Diário de Uma Paixão - Rachel McAdams
(7, 10), -- Diário de Uma Paixão - Ryan Gosling
(8, 11), -- Continências do Amor - Sofia Carson
(10, 12),-- Invocação do Mal - Vera Farmiga
(10, 13),-- Invocação do Mal - Patrick Wilson
(11, 14),-- O Silêncio - Kiernan Shipka
(12, 15),-- Cargo - Martin Freeman
(13, 16),-- Esposa de Mentirinha - Adam Sandler
(13, 18),-- Esposa de Mentirinha - Jennifer Aniston
(14, 16),-- Primeira Vez - Adam Sandler
(14, 17),-- Primeira Vez - Drew Barrymore
(15, 16),-- Gente Grande - Adam Sandler
(16, 16),-- Bat Mitzvá - Adam Sandler
(16, 19),-- Bat Mitzvá - Jackie Sandler
(17, 20),-- Enrolados - Zachary Levi
(17, 21),-- Enrolados - Mandy Moore
(20, 22),-- O Bom Gigante Amigo - Mark Rylance
(21, 23),-- A Lista da Minha Vida - Dakota Johnson
(22, 24),-- A Cinco Passos de Você - Cole Sprouse
(23, 25),-- Como Eu Era Antes de Você - Emilia Clarke
(24, 26);-- O Sol da Meia Noite - Bella Thorne

-- Filme e Linguagem
INSERT INTO linguagem_filme (id_filme, id_linguagem) VALUES
(1, 2),  -- Missão: Impossível (Inglês)
(2, 2),  -- Vingadores: Ultimato (Inglês)
(3, 2),  -- Batman (Inglês)
(4, 2),  -- Velozes e Furiosos (Inglês)
(5, 2),  -- Simplesmente Acontece (Inglês)
(6, 2),  -- Para Todos os Garotos (Inglês)
(7, 2),  -- Diário de Uma Paixão (Inglês)
(8, 2),  -- Continências do Amor (Inglês)
(9, 2),  -- Annabelle (Inglês)
(10, 2), -- Invocação do Mal (Inglês)
(11, 2), -- O Silêncio (Inglês)
(12, 2), -- Cargo (Inglês)
(13, 2), -- Esposa de Mentirinha (Inglês)
(14, 2), -- Como se Fosse a Primeira Vez (Inglês)
(15, 2), -- Gente Grande (Inglês)
(16, 2), -- Você Não Tá Convidada (Inglês)
(17, 2), -- Enrolados (Inglês)
(18, 2), -- Bambi (Inglês)
(19, 2), -- Barbie: Escola de Princesas (Inglês)
(20, 2), -- O Bom Gigante Amigo (Inglês)
(21, 3), -- A Lista da Minha Vida (Espanhol)
(22, 2), -- A Cinco Passos de Você (Inglês)
(23, 2), -- Como Eu Era Antes de Você (Inglês)
(24, 2); -- O Sol da Meia Noite (Inglês)

UPDATE filme SET status = 'aprovado';

SELECT * FROM usuarios;