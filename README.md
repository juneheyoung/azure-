# 📋 프로젝트명

운영 생산성 증가를 위한 쿼리 생성 agent

# 🎯 개요 및 목적

각 도메인별 운영자가 테이블 스키마 구조 입력을 통한 Knowledge 생성 Knowlegde 임베딩을 통한 RAG 적용하여 운영자의 질의에 적합한 쿼리문 생성

# 🎪 주요 기능

## 1. 지식정보 생성

지원 형식: TXT, JSON, DDL
전처리: 스키마 구조 분석 및 정규화
LLM 연동: 스키마 정보를 구조화된 지식으로 변환

## 2. 지식정보 저장

임베딩 모델 활용
검색알고리즘 : similarity_score_threshold, max_marginal_relevance_search (HYBRID)

## 3. 사용자(운영자) 질의

# 🏗️ 파이프라인

DB 스키마 입력 → LLM 정리 → 지식정보 생성
지식정보 입력 -> 임베딩 → Vector DB 저장
사용 지식정보 선택 및 사용자 질의 → 유사도 검색 → LLM 답변

# 기대 효과

운영하는 서비스에 대한 맞춤형 쿼리 생성을 통한 운영 생산성 향상
쿼리 작성 시간 단축

# 구현 시 고려사항

LLM의 할루시네이션을 최소화 시킬 수 있도록 프롬프트 구성

- 지식 정보 생성 시 입력 방법에 따른 구분, 옵션 구분

---

SAMPLE CASE

CREATE TABLE Users (
user_id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) NOT NULL UNIQUE,
email VARCHAR(100) NOT NULL UNIQUE,
password_hash VARCHAR(255) NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Posts (
post_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT NOT NULL,
title VARCHAR(200) NOT NULL,
content TEXT NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);
CREATE TABLE Comments (
comment_id INT AUTO_INCREMENT PRIMARY KEY,
post_id INT NOT NULL,
user_id INT NOT NULL,
content TEXT NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE,
FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE SET NULL
);

❓질문 1:
"어떤 사용자가 가장 많은 게시글을 작성했으며, 몇 개를 작성했나요?" 조회하는 쿼리문 작성해줘

사용된 테이블: Users, Posts

설명: 사용자의 게시글 수를 집계하고 가장 많이 작성한 사용자 정보를 조회합니다.

❓질문 2:
"가장 최근에 작성된 댓글의 내용과 해당 댓글을 작성한 사용자 이름, 그리고 댓글이 달린 게시글 제목은 무엇인가요?"

사용된 테이블: Comments, Users, Posts

설명: 최신 댓글 정보를 바탕으로 관련 사용자와 게시글 정보를 함께 조회합니다.
