import math

from tests.data.course_intervals import (
    POINTS_B_TO_C_DATA,
    POINTS_A_TO_B_DATA,
    POINTS_A_TO_C_DATA
)
from tests.data.places import (
    PLACE_A_DATA,
    PLACE_B_DATA,
    PLACE_C_DATA
)
from tests.factories import (
    PlaceFactory,
    CourseIntervalDifficultyFactory,
    CourseIntervalFactory,
    CourseFactory,
    CourseDifficultyFactory,
    CourseStyleFactory, CourseImageFactory
)


def setup_course_data_no_1():
    # given
    place_a = PlaceFactory.create(**PLACE_A_DATA)
    place_b = PlaceFactory.create(**PLACE_B_DATA)
    place_c = PlaceFactory.create(**PLACE_C_DATA)

    difficulty_lv1 = CourseIntervalDifficultyFactory.create(level=1)
    difficulty_lv2 = CourseIntervalDifficultyFactory.create(level=2)

    interval_a_to_b = CourseIntervalFactory.create(
        difficulty=difficulty_lv1,
        place_a=place_a,
        place_b=place_b,
        points=POINTS_A_TO_B_DATA
    )
    interval_b_to_c = CourseIntervalFactory.create(
        difficulty=difficulty_lv2,
        place_a=place_b,
        place_b=place_c,
        points=POINTS_B_TO_C_DATA
    )
    interval_a_to_c = CourseIntervalFactory.create(
        difficulty=difficulty_lv1,
        place_a=place_a,
        place_b=place_c,
        points=POINTS_A_TO_C_DATA
    )

    course = CourseFactory.create(
        name="관악산 일부 코스",
        course_difficulty=CourseDifficultyFactory.create(),
        course_style=CourseStyleFactory.create(),
        links=[
            {"interval": interval_a_to_b, "position": 1, "is_reversed": False},
            {"interval": interval_b_to_c, "position": 2, "is_reversed": False},
            {"interval": interval_a_to_c, "position": 3, "is_reversed": True},
        ]
    )
    CourseImageFactory.create(sort_order=1, course_id=course.id)
    CourseImageFactory.create(sort_order=2, course_id=course.id)

    total_length = (
            interval_a_to_b.length_m
            + interval_b_to_c.length_m
            + interval_a_to_c.length_m
    )
    duration = (
            interval_a_to_b.duration_ab_minutes
            + interval_b_to_c.duration_ab_minutes
            + interval_a_to_c.duration_ba_minutes
    )

    print("====")
    print(total_length, duration)

    return math.floor(total_length / 1000 * 10) / 10, duration
