# backend/app/navigation/dependencies.py

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import get_database

from app.navigation.repositories import (
    BuildingRepository,
    RoomRepository,
    LandmarkRepository,
    FacilityRepository,
    PathwayRepository
)
from app.navigation.services import (
    BuildingService,
    RoomService,
    LandmarkService,
    FacilityService,
    PathwayService,
    NavigationSearchService
)

# Repositories
def get_building_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> BuildingRepository:
    return BuildingRepository(db)

def get_room_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> RoomRepository:
    return RoomRepository(db)

def get_landmark_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> LandmarkRepository:
    return LandmarkRepository(db)

def get_facility_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> FacilityRepository:
    return FacilityRepository(db)

def get_pathway_repo(db: AsyncIOMotorDatabase = Depends(get_database)) -> PathwayRepository:
    return PathwayRepository(db)

# Services
def get_building_service(repo: BuildingRepository = Depends(get_building_repo)) -> BuildingService:
    return BuildingService(repo)

def get_room_service(
    repo: RoomRepository = Depends(get_room_repo),
    b_repo: BuildingRepository = Depends(get_building_repo)
) -> RoomService:
    return RoomService(repo, b_repo)

def get_landmark_service(repo: LandmarkRepository = Depends(get_landmark_repo)) -> LandmarkService:
    return LandmarkService(repo)

def get_facility_service(repo: FacilityRepository = Depends(get_facility_repo)) -> FacilityService:
    return FacilityService(repo)

def get_pathway_service(repo: PathwayRepository = Depends(get_pathway_repo)) -> PathwayService:
    return PathwayService(repo)

def get_nav_search_service(
    b_repo: BuildingRepository = Depends(get_building_repo),
    r_repo: RoomRepository = Depends(get_room_repo),
    l_repo: LandmarkRepository = Depends(get_landmark_repo),
    f_repo: FacilityRepository = Depends(get_facility_repo)
) -> NavigationSearchService:
    return NavigationSearchService(b_repo, r_repo, l_repo, f_repo)
