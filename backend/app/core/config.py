from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "LightMes Backend"
    # 默认生产环境：dev 必须显式配置，防止漏配导致异常堆栈泄露给客户端
    APP_ENV: str = "prod"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DB_URL: str = "mysql+pymysql://root:root@127.0.0.1:3306/lightmes?charset=utf8mb4"
    DB_ECHO: bool = False
    DB_AUTO_CREATE: bool = True
    DB_AUTO_SEED: bool = True

    # 无默认密钥：漏配时启动即失败，避免使用公开已知值伪造 token
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    # 未勾选「记住登录」：8 小时
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    # 勾选「记住登录」：7 天
    REMEMBER_ME_EXPIRE_MINUTES: int = 10080
    PUBLIC_BASE_URL: str = ""
    # 员工 H5 外网地址（用于任务标签二维码，如 https://h5.example.com）
    H5_PUBLIC_BASE_URL: str = ""

    STORAGE_DRIVER: str = "local"
    STORAGE_LOCAL_ROOT: str = "./data/storage"
    FILE_MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    FILE_ALLOWED_MIME: str = (
        "image/jpeg,image/png,image/webp,application/pdf,"
        "video/mp4,video/quicktime,video/webm,video/3gpp,video/x-msvideo"
    )

    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/1"
    CELERY_TIMEZONE: str = "Asia/Shanghai"
    CELERY_ENABLE_UTC: bool = True

    CRM_PUBLIC_POOL_RECYCLE_HOUR: int = 2
    CRM_PUBLIC_POOL_RECYCLE_MINUTE: int = 0

    ALIYUN_OSS_ENDPOINT: str = ""
    ALIYUN_OSS_REGION: str = ""
    ALIYUN_OSS_BUCKET: str = ""
    ALIYUN_OSS_ACCESS_KEY_ID: str = ""
    ALIYUN_OSS_ACCESS_KEY_SECRET: str = ""

    TENCENT_COS_ENDPOINT: str = ""
    TENCENT_COS_REGION: str = ""
    TENCENT_COS_BUCKET: str = ""
    TENCENT_COS_SECRET_ID: str = ""
    TENCENT_COS_SECRET_KEY: str = ""

    QINIU_KODO_ENDPOINT: str = ""
    QINIU_KODO_REGION: str = ""
    QINIU_KODO_BUCKET: str = ""
    QINIU_KODO_ACCESS_KEY: str = ""
    QINIU_KODO_SECRET_KEY: str = ""

    AI_ENABLED: bool = False
    AI_BASE_URL: str = ""
    AI_API_KEY: str = ""
    AI_DEFAULT_MODEL: str = ""
    AI_TIMEOUT_SECONDS: int = 120
    # RAG 向量搜索
    RAG_CHROMA_DIR: str = "./data/chroma_db"
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_HYBRID_WEIGHT: float = 0.7
    RAG_EMBEDDING_MODEL: str = ""

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        """生产环境强制要求强随机 JWT_SECRET，禁止使用默认/空值（fail fast）。"""
        if self.APP_ENV != "dev" and (not self.JWT_SECRET or self.JWT_SECRET in ("change_me", "secret", "123456")):
            raise ValueError("生产环境必须配置强随机 JWT_SECRET（如 openssl rand -hex 32 生成）")
        return self


settings = Settings()
