from pydantic import BaseModel, Field, EmailStr

from model.User import Users


class UserSchema(BaseModel):
    email: EmailStr = Field()
    password: str = Field()

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: EmailStr = Field()
    password: str = Field()


class UserInfo:
    def get_user_by_email(email, db):
        return db.query(Users).filter(Users.email == email).first()

    def get_user_by_email_and_password(email, password, db):
        return (
            db.query(Users)
            .filter(Users.email == email, Users.password == password)
            .first()
        )

    def create_user(user, db):
        db_user = UserInfo.get_user_by_email(email=user.email, db=db)
        if db_user:
            return {"success": False, "error": "User already exist"}

        user = Users(email=user.email, password=user.password)
        db.add(user)
        db.commit()
        db.refresh(user)

        return {"success": True, "user": user}

    def check_user(user, db):
        db_user = UserInfo.get_user_by_email_and_password(
            email=user.email, password=user.password, db=db
        )
        if db_user:
            return True

        return False
