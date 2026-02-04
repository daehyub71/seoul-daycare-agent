"""
SQLAlchemy ORM models for Seoul Daycare database
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DaycareCenter(Base):
    """어린이집 정보 모델"""

    __tablename__ = "daycare_centers"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 기본 정보
    stcode = Column(String(20), unique=True, nullable=False, index=True)  # 어린이집코드
    crname = Column(String(255), nullable=False)  # 어린이집명
    crtypename = Column(String(50), index=True)  # 어린이집유형
    crstatusname = Column(String(50), index=True)  # 운영현황
    craddr = Column(Text)  # 주소
    sigunname = Column(String(50), index=True)  # 시군구명
    zipcode = Column(String(10))  # 우편번호
    la = Column(Float)  # 위도
    lo = Column(Float)  # 경도
    crtelno = Column(String(50))  # 전화번호
    crfaxno = Column(String(50))  # 팩스번호
    crhome = Column(String(255))  # 홈페이지

    # 운영 정보
    crcapat = Column(Integer)  # 정원
    crchcnt = Column(Integer)  # 현원
    crcnfmdt = Column(String(20))  # 인가일자
    crabldt = Column(String(20))  # 폐지일자
    crpausebegindt = Column(String(20))  # 휴지시작일
    crpauseenddt = Column(String(20))  # 휴지종료일

    # 특수 서비스
    crspec = Column(String(255))  # 제공서비스
    crcargbname = Column(String(50))  # 통학차량운영여부

    # 시설 정보
    nrtrroomcnt = Column(Integer)  # 보육실수
    nrtrroomsize = Column(Float)  # 보육실면적
    plgrdco = Column(Integer)  # 놀이터수
    cctvinstlcnt = Column(Integer)  # CCTV총설치수

    # 교직원 정보
    chcrtescnt = Column(Integer)  # 보육교직원수
    em_cnt_tot = Column(Integer)  # 교직원총계
    em_cnt_a1 = Column(Integer)  # 원장
    em_cnt_a2 = Column(Integer)  # 보육교사
    em_cnt_a3 = Column(Integer)  # 특수교사
    em_cnt_a4 = Column(Integer)  # 치료교사
    em_cnt_a5 = Column(Integer)  # 영양사
    em_cnt_a6 = Column(Integer)  # 간호사
    em_cnt_a7 = Column(Integer)  # 조리원
    em_cnt_a8 = Column(Integer)  # 사무직원
    em_cnt_a10 = Column(Integer)  # 간호조무사

    # 근속년수
    em_cnt_0y = Column(Integer)  # 1년미만
    em_cnt_1y = Column(Integer)  # 1년이상~2년미만
    em_cnt_2y = Column(Integer)  # 2년이상~4년미만
    em_cnt_4y = Column(Integer)  # 4년이상~6년미만
    em_cnt_6y = Column(Integer)  # 6년이상

    # 아동 정보 (연령별)
    child_cnt_tot = Column(Integer)  # 아동수총계
    child_cnt_00 = Column(Integer)  # 만0세
    child_cnt_01 = Column(Integer)  # 만1세
    child_cnt_02 = Column(Integer)  # 만2세
    child_cnt_03 = Column(Integer)  # 만3세
    child_cnt_04 = Column(Integer)  # 만4세
    child_cnt_05 = Column(Integer)  # 만5세
    child_cnt_m2 = Column(Integer)  # 영아혼합(만0~2세)
    child_cnt_m5 = Column(Integer)  # 유아혼합(만3~5세)
    child_cnt_sp = Column(Integer)  # 특수장애

    # 반 정보
    class_cnt_tot = Column(Integer)  # 반수총계
    class_cnt_00 = Column(Integer)  # 만0세반
    class_cnt_01 = Column(Integer)  # 만1세반
    class_cnt_02 = Column(Integer)  # 만2세반
    class_cnt_03 = Column(Integer)  # 만3세반
    class_cnt_04 = Column(Integer)  # 만4세반
    class_cnt_05 = Column(Integer)  # 만5세반
    class_cnt_m2 = Column(Integer)  # 영아혼합반
    class_cnt_m5 = Column(Integer)  # 유아혼합반
    class_cnt_sp = Column(Integer)  # 특수장애반

    # 메타데이터
    datastdrdt = Column(String(20))  # 데이터기준일자
    work_dttm = Column(String(20))  # 데이터수집일

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<DaycareCenter(stcode={self.stcode}, crname={self.crname}, crtypename={self.crtypename})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "stcode": self.stcode,
            "crname": self.crname,
            "crtypename": self.crtypename,
            "crstatusname": self.crstatusname,
            "craddr": self.craddr,
            "sigunname": self.sigunname,
            "zipcode": self.zipcode,
            "la": self.la,
            "lo": self.lo,
            "crtelno": self.crtelno,
            "crfaxno": self.crfaxno,
            "crhome": self.crhome,
            "crcapat": self.crcapat,
            "crchcnt": self.crchcnt,
            "crcnfmdt": self.crcnfmdt,
            "crabldt": self.crabldt,
            "crpausebegindt": self.crpausebegindt,
            "crpauseenddt": self.crpauseenddt,
            "crspec": self.crspec,
            "crcargbname": self.crcargbname,
            "nrtrroomcnt": self.nrtrroomcnt,
            "nrtrroomsize": self.nrtrroomsize,
            "plgrdco": self.plgrdco,
            "cctvinstlcnt": self.cctvinstlcnt,
            "chcrtescnt": self.chcrtescnt,
            "em_cnt_tot": self.em_cnt_tot,
            "em_cnt_a1": self.em_cnt_a1,
            "em_cnt_a2": self.em_cnt_a2,
            "child_cnt_tot": self.child_cnt_tot,
            "child_cnt_00": self.child_cnt_00,
            "child_cnt_01": self.child_cnt_01,
            "child_cnt_02": self.child_cnt_02,
            "child_cnt_03": self.child_cnt_03,
            "child_cnt_04": self.child_cnt_04,
            "child_cnt_05": self.child_cnt_05,
            "class_cnt_tot": self.class_cnt_tot,
            "class_cnt_00": self.class_cnt_00,
            "class_cnt_01": self.class_cnt_01,
            "class_cnt_02": self.class_cnt_02,
            "class_cnt_03": self.class_cnt_03,
            "class_cnt_04": self.class_cnt_04,
            "class_cnt_05": self.class_cnt_05,
            "datastdrdt": self.datastdrdt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_embedding_text(self) -> str:
        """
        Generate text for embedding (어린이집명 + 주소 + 유형 + 제공서비스)
        """
        parts = []

        if self.crname:
            parts.append(self.crname)
        if self.craddr:
            parts.append(self.craddr)
        if self.crtypename:
            parts.append(self.crtypename)
        if self.crspec:
            parts.append(self.crspec)

        return " ".join(parts)
