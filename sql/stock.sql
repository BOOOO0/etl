CREATE TABLE stock_daily_data (
    id INT AUTO_INCREMENT PRIMARY KEY, -- 기본 키
    company_name VARCHAR(100) NOT NULL, -- 회사 이름
    symbol VARCHAR(10) NOT NULL,        -- 주식 심볼
    stck_prdy_clpr INT NOT NULL,        -- 종가
    stck_oprc INT NOT NULL,             -- 시가
    stck_hgpr INT NOT NULL,             -- 고가
    stck_lwpr INT NOT NULL,             -- 저가
    acml_vol INT NOT NULL,              -- 누적 거래량
    ingestion_time DATETIME NOT NULL    -- 적재 시간
);
