from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    """User account model for authentication and data ownership."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    # Relationships
    profiles: Mapped[List["UserProfileRecord"]] = relationship(
        "UserProfileRecord", back_populates="user", cascade="all, delete-orphan"
    )
    food_logs: Mapped[List["FoodLog"]] = relationship(
        "FoodLog", back_populates="user", cascade="all, delete-orphan"
    )
    meal_plans: Mapped[List["MealPlan"]] = relationship(
        "MealPlan", back_populates="user", cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["FoodRecommendation"]] = relationship(
        "FoodRecommendation", back_populates="user", cascade="all, delete-orphan"
    )


class UserProfileRecord(Base):
    """Persisted user profile for personalized nutrition and meal planning."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)

    activity_level: Mapped[str] = mapped_column(String(30), nullable=False)
    goal: Mapped[str] = mapped_column(String(30), nullable=False)
    dietary_preference: Mapped[str] = mapped_column(String(30), nullable=False)

    allergies: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    dietary_restrictions: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    disliked_foods: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    preferred_cuisine: Mapped[str] = mapped_column(String(60), nullable=False, default="Any")
    meals_per_day: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="profiles")


class FoodItem(Base):
    """Catalog of verified and user-contributed food items with nutrition."""

    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    cuisine: Mapped[str] = mapped_column(String(60), index=True, nullable=False, default="Any")
    diet_type: Mapped[str] = mapped_column(String(40), index=True, nullable=False, default="vegetarian")

    calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sugar_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    serving_size_g: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    serving_unit: Mapped[str] = mapped_column(String(80), nullable=False, default="1 serving (100g)")

    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    health_label: Mapped[str | None] = mapped_column(String(50), nullable=True)

    ingredients: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    allergens: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )


class FoodRecommendation(Base):
    """Persisted recommendation runs with targets, suggested meals, and reasoning."""

    __tablename__ = "food_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    profile_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )

    recommendation_type: Mapped[str] = mapped_column(String(60), nullable=False, default="daily_targets")
    goal: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_calories_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)

    recommended_items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    target_macros: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="recommendations")


class MealPlan(Base):
    """Daily or multi-meal plans with targets and nutrition aggregates."""

    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    profile_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("user_profiles.id", ondelete="SET NULL"), nullable=True, index=True
    )

    plan_name: Mapped[str] = mapped_column(String(150), nullable=False, default="Daily Meal Plan")
    plan_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    goal: Mapped[str | None] = mapped_column(String(50), nullable=True)

    target_calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    planned_calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)

    meals_data: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    nutrition_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="meal_plans")


class FoodLog(Base):
    """Consumed meal records for tracking daily intake and nutrient aggregates."""

    __tablename__ = "food_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    dish_name: Mapped[str] = mapped_column(String(255), nullable=False)
    meal_type: Mapped[str] = mapped_column(String(50), nullable=False, default="lunch")
    portion_weight_g: Mapped[float] = mapped_column(Float, nullable=False, default=250.0)

    calories_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fiber_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sugar_g: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    health_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    logged_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp(), nullable=False
    )

    user: Mapped[Optional["User"]] = relationship("User", back_populates="food_logs")


class MealAnalysis(Base):
    """Preserved AI food recognition & estimated nutrition analysis records."""

    __tablename__ = "meal_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dish_name: Mapped[str] = mapped_column(String(255), nullable=False)
    portion_weight_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    calories_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    fiber_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    health_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False,
    )
