import { getPaginationItems } from "@/lib/pagination";
import { useEffect, useState } from "react";
import type { CourseSearchResponseSchema } from "@/types/responses/course-list";
import { COURSE_DIFFICULTY_COLORS } from "@/vars/colors";

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
        <div className="mt-5 w-full lg:w-[700px]">
            {/* Course Card List */}
            <div className="flex flex-col gap-3">
                {courses.map((course) => (
                    <a
                        key={course.id}
                        href={`/courses/${course.id}`}
                        className="flex items-center gap-4 p-4 rounded-box border border-base-content/10 bg-base-100 hover:shadow-md transition-shadow"
                    >
                        {/* Difficulty Badge */}
                        <div
                            className="text-white px-2 py-1.5 rounded-md text-center min-w-12 text-sm font-bold shrink-0"
                            style={{ backgroundColor: COURSE_DIFFICULTY_COLORS[course.difficulty.level] }}
                        >
                            Lv.{course.difficulty.level}
                        </div>

                        {/* Course Info */}
                        <div className="flex-1 min-w-0">
                            <div className="font-bold text-base truncate">{course.name}</div>
                            <div className="text-sm text-base-content/60 truncate">
                                {course.roadAddresses.length > 0 ? course.roadAddresses[0] : course.loadAddresses[0]}
                            </div>
                        </div>

                        {/* Course Style Tag */}
                        <div className="badge badge-outline shrink-0">{course.courseStyle.name}</div>
                    </a>
                ))}
            </div>

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