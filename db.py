# MongoDB 연결. 다른 파일에서는 이렇게 쓴다.
#   from db import get_db
#   db = get_db()
#   db.news.insert_one({...})
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def get_db():
    return db


def create_indexes():
    # 같은 기사, 같은 통계가 두 번 저장되지 않게 막는다 (여러 번 실행해도 괜찮음)
    db.news.create_index("link", unique=True)
    db.stats.create_index([("type", 1), ("year", 1), ("group", 1)], unique=True)


if __name__ == "__main__":
    # 연결 테스트: python db.py
    create_indexes()
    print("MongoDB 연결 성공:", DB_NAME)
    print("stats 문서 수:", db.stats.count_documents({}))
    print("news 문서 수:", db.news.count_documents({}))
