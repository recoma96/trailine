import { useEffect, useState } from "react";


type DifficultySchema = {
    id: number;
    code: string;
    name: string;
    level: number;
};

type StyleSchema = {
    id: number;
    code: string;
    name: string;
};

type CourseSchema = {
    courseStyle: StyleSchema;
    difficulty: DifficultySchema;
    id: number;
    name: string;
    loadAddresses: string[];
    roadAddresses: string[];
};


const CourseSearchList: React.FC = () => {
    const [courses, setCourses] = useState<CourseSchema[]>([]);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const requestParams = new URLSearchParams();

        const word = urlParams.get("word");
        const difficulty = urlParams.get("difficulty");
        const courseStyle = urlParams.get("courseStyle");
        const page = urlParams.get("page") || "1";
        const pageSize = urlParams.get("pageSize") || "10";
        
        requestParams.append("page", page);
        requestParams.append("pageSize", pageSize);
        if (word) {
            requestParams.append("word", word);
        }
        if (difficulty && difficulty !== "0") {
            requestParams.append("difficulty", difficulty);
        }
        if (courseStyle && courseStyle !== "0") {
            requestParams.append("courseStyle", courseStyle);
        }

        const fetchCourses = async () => {
            try {
                const response = await fetch(`${import.meta.env.PUBLIC_API_ENDPOINT}/v1/courses?${requestParams.toString()}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch courses');
                }
                const raw = await response.json();
                const data: CourseSchema[] = raw.courses;
                setCourses(data);
            } catch (error) {
                console.error("Error fetching courses:", error);
            }
        }
        fetchCourses();
    }, []);

    return (
        <div className="mt-5 overflow-xauto rounded-box border border-base-content/5 bg-base-100 w-full lg:w-[700px]">
            <table className="table">
                <thead>
                    <tr>
                        <th></th>
                        <th>코스명</th>
                        <th>주소</th>
                        <th>코스 스타일</th>
                        <th>난이도</th>
                    </tr>
                </thead>
                <tbody>
                    {courses.map((course, index) => (
                        <tr key={course.id}>
                            <th>{index + 1}</th>
                            <td><a href={`/courses/${course.id}`} className="hover:underline">{course.name}</a></td>
                            <td>
                                {course.roadAddresses.length > 0 ? (
                                    course.roadAddresses[0]
                                ) : (
                                    course.loadAddresses[0]
                                )}
                            </td>
                            <td>{course.courseStyle.name}</td>
                            <td>Lv.{course.difficulty.level}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
};

export default CourseSearchList;