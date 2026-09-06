# Agorapulse Connector — Discovery & API Specification

**Vendor:** Agorapulse  
**Catalog URL:** https://agorapulse.com  
**API Base URL:** `https://api.agorapulse.com/v1`  
**Authentication:** OAuth 2.0 Bearer Token

## Core Entities & Endpoints
аккаунты соцсетей (/accounts), входящие сообщения инбокса (/inbox), запланированные публикации, отчеты

## Verified Read Operation
- **Эндпоинт проверки:** `GET /v1/accounts`
- **Метод:** GET
- **Ожидаемый ответ:** HTTP 200 OK со структурой метаданных сущности.

## Rate Limits & Pagination
- Стандартная курсорная или offset/limit пагинация вендора.
- Обработка HTTP 429 Too Many Requests с экспоненциальным backoff.
- Защита от тайм-аутов: ограничение на сетевые запросы 15-30 секунд.
