import { getPaginationItems } from "@/utils";
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

type CourseSearchResponseSchema = {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    courses: CourseSchema[];
}


const CourseSearchList: React.FC = () => {
    const [searchResult, setSearchResult] = useState<CourseSearchResponseSchema | null>(null);

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
                const jsonResponse: CourseSearchResponseSchema = await response.json();
                setSearchResult(jsonResponse);
            } catch (error) {
                console.error("Error fetching courses:", error);
            }
        }
        fetchCourses();
    }, []);

    const handlePageChange = (page: string) => {
        if (page === "...") return;

        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set("page", page);
        window.location.search = urlParams.toString();
    }
    
    const courses = searchResult?.courses || [];
    const currentPage = searchResult?.page || 1;
    const totalPages = searchResult?.totalPages || 1;
    const paginationItems = getPaginationItems(currentPage, totalPages);

    return (
        <div className="mt-5 overflow-xauto rounded-box bg-base-100 w-full lg:w-[700px]">
            <table className="table border border-base-content/5">
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
                            <th>{((currentPage - 1) * (searchResult?.pageSize || 10)) + index + 1}</th>
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
            
            {/* Pagination */}
            <div className="text-center mt-10">
                <div className="join">
                    {paginationItems.map((page, index) => (
                        <button 
                            key={index}
                            className={`join-item btn ${page === '...' ? 'btn-disabled' : ''} ${page === currentPage.toString() ? 'btn-active' : ''}`}
                            onClick={() => handlePageChange(page)}
                        >
                            {page}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
};

export default CourseSearchList;