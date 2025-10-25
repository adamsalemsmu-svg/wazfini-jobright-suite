from fastapi import APIRouter, Depends
from sqlalchemy import select
from ..schemas import ProfileIn
from ..models import User, Profile, Experience, Education, Skill
from ..core.db import get_session

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/upsert")
async def upsert_profile(payload: ProfileIn, db=Depends(get_session)):
    user = (
        (await db.execute(select(User).where(User.email == payload.user_email)))
        .scalars()
        .first()
    )
    if not user:
        user = User(email=payload.user_email, name=payload.name)
        db.add(user)
        await db.flush()

    profile = (
        (await db.execute(select(Profile).where(Profile.user_id == user.id)))
        .scalars()
        .first()
    )
    if not profile:
        profile = Profile(user_id=user.id)
        db.add(profile)
        await db.flush()

    for f in ["phone", "address", "linkedin", "github", "summary"]:
        setattr(profile, f, getattr(payload, f))

    # clear and repopulate
    await db.execute(
        Experience.__table__.delete().where(Experience.profile_id == profile.id)
    )
    await db.execute(
        Education.__table__.delete().where(Education.profile_id == profile.id)
    )
    await db.execute(Skill.__table__.delete().where(Skill.profile_id == profile.id))

    for e in payload.experiences:
        db.add(Experience(profile_id=profile.id, **e.model_dump()))
    for e in payload.educations:
        db.add(Education(profile_id=profile.id, **e.model_dump()))
    for s in payload.skills:
        db.add(Skill(profile_id=profile.id, name=s))

    await db.commit()
    return {"ok": True, "profile_id": profile.id}
