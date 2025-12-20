interface DifficultySchema {
    id: number;
    code: string;
    name: string;
    level: number;
};

interface StyleSchema {
    id: number;
    code: string;
    name: string;
};

interface CourseSchema {
    courseStyle: StyleSchema;
    difficulty: DifficultySchema;
    id: number;
    name: string;
    loadAddresses: string[];
    roadAddresses: string[];
};

export interface CourseSearchResponseSchema {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
    courses: CourseSchema[];
}
